import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProducts } from '../hooks/useProducts';
import ProductDetail from '../components/product/ProductDetail';
import ProductGrid from '../components/product/ProductGrid';

const ProductDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  
  const {
    currentProduct,
    loading,
    error,
    fetchProductBySlug,
    resetCurrentProduct,
    fetchProducts,
    products,
  } = useProducts();
  
  useEffect(() => {
    if (slug) {
      fetchProductBySlug(slug);
    }
    
    return () => {
      resetCurrentProduct();
    };
  }, [slug, fetchProductBySlug, resetCurrentProduct]);
  
  useEffect(() => {
    if (error) {
      navigate('/not-found', { replace: true });
    }
  }, [error, navigate]);
  
  useEffect(() => {
    if (currentProduct) {
      // Fetch related products based on category
      if (currentProduct.category_id) {
        fetchProducts({
          category_id: currentProduct.category_id,
          page: 1,
          size: 4,
        });
      }
    }
  }, [currentProduct, fetchProducts]);
  
  if (loading && !currentProduct) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="aspect-square bg-gray-200 rounded-lg"></div>
            <div>
              <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-6 bg-gray-200 rounded w-1/2 mb-6"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-6"></div>
              <div className="h-10 bg-gray-200 rounded w-full mb-4"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  if (!currentProduct && !loading) {
    return null; // Will redirect to not-found page due to the error effect
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      {currentProduct && <ProductDetail product={currentProduct} />}
      
      {/* Related Products */}
      {products && products.items.length > 0 && (
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Related Products</h2>
          <ProductGrid
            products={products.items.filter(item => item.id !== currentProduct?.id).slice(0, 4)}
            loading={loading}
            columns={4}
            emptyMessage="No related products found"
          />
        </div>
      )}
    </div>
  );
};

export default ProductDetailPage;