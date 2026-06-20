import { getCatalogData } from "@/lib/catalog";
import MerchBuilderClient from "./MerchBuilderClient";

export default function MerchBuilderPage() {
  const { products, kits, categories } = getCatalogData();
  
  return (
    <MerchBuilderClient 
      initialProducts={products} 
      initialKits={kits} 
      initialCategories={categories} 
    />
  );
}
