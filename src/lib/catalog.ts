import fs from 'fs';
import path from 'path';
import * as xlsx from 'xlsx';
import { Product, Kit } from '@/types';

// Helper to safely parse JSON from Excel strings
const safeParseJSON = (str: any, fallback: any = []) => {
  if (typeof str !== 'string') return str || fallback;
  try {
    return JSON.parse(str);
  } catch (e) {
    return fallback;
  }
};

const safeSplit = (str: any, fallback: any = []) => {
  if (typeof str !== 'string') return fallback;
  return str.split(',').map((s: string) => s.trim()).filter(Boolean);
};

export function getCatalogData() {
  const excelPath = path.join(process.cwd(), 'catalog.xlsx');
  
  if (!fs.existsSync(excelPath)) {
    console.warn("catalog.xlsx not found, returning empty arrays");
    return { products: [], kits: [], categories: [] };
  }

  const workbook = xlsx.readFile(excelPath);
  
  // Parse Products
  let rawProducts: any[] = [];
  if (workbook.SheetNames.includes('Products')) {
    rawProducts = xlsx.utils.sheet_to_json(workbook.Sheets['Products']);
  }
  
  // Parse Kits
  let rawKits: any[] = [];
  if (workbook.SheetNames.includes('Kits')) {
    rawKits = xlsx.utils.sheet_to_json(workbook.Sheets['Kits']);
  }

  const products: Product[] = rawProducts.map((row) => {
    // Check if gallery folder exists
    const galleryPath = path.join(process.cwd(), 'public', 'galleries', 'products', String(row.id));
    let localMain = null;
    let localGallery: string[] = [];
    
    if (fs.existsSync(galleryPath)) {
      const files = fs.readdirSync(galleryPath).filter(f => !f.startsWith('.'));
      const mainFile = files.find(f => f.toLowerCase().startsWith('main.'));
      if (mainFile) {
        localMain = `/galleries/products/${row.id}/${mainFile}`;
      }
      localGallery = files
        .filter(f => f !== mainFile)
        .map(f => `/galleries/products/${row.id}/${f}`);
    }

    // Fallback to Excel media if local doesn't exist
    const excelMedia = safeParseJSON(row.media, {});

    return {
      id: String(row.id),
      name: String(row.name),
      category: String(row.category || 'Uncategorized'),
      subcategory: String(row.subcategory || ''),
      description: String(row.description || ''),
      basePrice: Number(row.basePrice || 0),
      tiers: safeParseJSON(row.tiers, []),
      media: {
        main: localMain || excelMedia.main || '',
        gallery: localGallery.length > 0 ? localGallery : (excelMedia.gallery || []),
        mockup: excelMedia.mockup || undefined
      },
      colorTags: safeSplit(row.colorTags, []),
      printOptions: safeSplit(row.printOptions, []),
      minOrderQty: Number(row.minOrderQty || 1),
      productionDays: Number(row.productionDays || 1),
      popular: Boolean(row.popular)
    };
  });

  const kits: Kit[] = rawKits.map((row) => {
    const galleryPath = path.join(process.cwd(), 'public', 'galleries', 'kits', String(row.id));
    let localCover = null;
    
    if (fs.existsSync(galleryPath)) {
      const files = fs.readdirSync(galleryPath).filter(f => !f.startsWith('.'));
      const coverFile = files.find(f => f.toLowerCase().startsWith('main.') || f.toLowerCase().startsWith('cover.'));
      if (coverFile) {
        localCover = `/galleries/kits/${row.id}/${coverFile}`;
      }
    }

    return {
      id: String(row.id),
      name: String(row.name),
      tagline: String(row.tagline || ''),
      description: String(row.description || ''),
      preset: String(row.preset || ''),
      coverImage: localCover || String(row.coverImage || ''),
      colorTag: String(row.colorTag || ''),
      items: safeParseJSON(row.items, [])
    };
  });

  // Extract unique categories
  const categoriesSet = new Set(products.map(p => p.category));
  const categories = Array.from(categoriesSet).filter(Boolean);

  return { products, kits, categories };
}
