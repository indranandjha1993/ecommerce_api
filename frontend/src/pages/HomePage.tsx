import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useProducts } from '../hooks/useProducts';
import { useCategories } from '../hooks/useCategories';
import { useBrands } from '../hooks/useBrands';
import ProductGrid from '../components/product/ProductGrid';
import Button from '../components/ui/Button';

const HomePage: React.FC = () => {
  const {
    featuredProducts,
    newArrivals,
    bestsellers,
    fetchFeaturedProducts,
    fetchNewArrivals,
    fetchBestsellers,
    loading,
  } = useProducts();
  
  const { topCategories, fetchTopCategories } = useCategories();
  const { topBrands, fetchTopBrands } = useBrands();
  
  useEffect(() => {
    fetchFeaturedProducts(8);
    fetchNewArrivals({ limit: 8 });
    fetchBestsellers({ limit: 8 });
    fetchTopCategories(6);
    fetchTopBrands(6);
  }, [
    fetchFeaturedProducts,
    fetchNewArrivals,
    fetchBestsellers,
    fetchTopCategories,
    fetchTopBrands,
  ]);
  
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-xl overflow-hidden shadow-xl -mx-4 sm:mx-0">
        <div className="absolute inset-0 overflow-hidden mix-blend-overlay">
          <img
            src="https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            alt="Hero background"
            className="w-full h-full object-cover object-center"
          />
        </div>
        <div className="relative px-6 py-16 sm:py-24 sm:px-12 flex flex-col items-center text-center sm:text-left sm:items-start">
          <div className="max-w-xl">
            <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl lg:text-5xl drop-shadow-md">
              Summer Collection 2023
            </h1>
            <p className="mt-4 sm:mt-6 text-lg sm:text-xl text-white text-opacity-90 drop-shadow">
              Discover our latest products with amazing deals and discounts.
              Shop now and get free shipping on all orders over $50.
            </p>
            <div className="mt-6 sm:mt-10 flex flex-wrap gap-4 justify-center sm:justify-start">
              <Link to="/products">
                <Button variant="primary" size="lg" className="bg-white text-blue-700 hover:bg-gray-100">
                  Shop Now
                </Button>
              </Link>
              <Link to="/categories">
                <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:bg-opacity-10">
                  Browse Categories
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
      
      {/* Featured Products */}
      <section className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Featured Products</h2>
          <Link to="/products?featured=true" className="text-blue-600 hover:text-blue-500 flex items-center">
            View All
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>
        <ProductGrid
          products={featuredProducts}
          loading={loading}
          columns={4}
        />
      </section>
      
      {/* Categories */}
      <section className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Shop by Category</h2>
            <p className="mt-1 text-gray-600">
              Browse our wide selection of products by category
            </p>
          </div>
          <Link to="/categories" className="text-blue-600 hover:text-blue-500 flex items-center">
            View All
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>
        
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {topCategories.map((category) => (
            <Link
              key={category.id}
              to={`/categories/${category.slug}`}
              className="group flex flex-col items-center"
            >
              <div className="aspect-square w-full rounded-lg overflow-hidden bg-gray-100 border border-gray-200 shadow-sm">
                {category.image_url ? (
                  <img
                    src={category.image_url}
                    alt={category.name}
                    className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-blue-50 text-blue-600">
                    <svg
                      className="h-10 w-10"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z" />
                    </svg>
                  </div>
                )}
              </div>
              <h3 className="mt-2 text-center font-medium text-gray-900 group-hover:text-blue-600 text-sm">
                {category.name}
              </h3>
            </Link>
          ))}
        </div>
      </section>
      
      {/* New Arrivals */}
      <section className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">New Arrivals</h2>
            <p className="mt-1 text-gray-600">
              Check out our latest products
            </p>
          </div>
          <Link to="/products?sort_by=created_at&sort_order=desc" className="text-blue-600 hover:text-blue-500 flex items-center">
            View All
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>
        <ProductGrid
          products={newArrivals}
          loading={loading}
          columns={4}
        />
      </section>
      
      {/* Brands */}
      <section className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Popular Brands</h2>
            <p className="mt-1 text-gray-600">
              Discover products from top brands
            </p>
          </div>
          <Link to="/brands" className="text-blue-600 hover:text-blue-500 flex items-center">
            View All
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>
        
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {topBrands.map((brand) => (
            <Link
              key={brand.id}
              to={`/brands/${brand.slug}`}
              className="flex flex-col items-center group"
            >
              <div className="aspect-square w-full rounded-lg overflow-hidden bg-white p-3 border border-gray-200 shadow-sm flex items-center justify-center">
                {brand.logo_url ? (
                  <img
                    src={brand.logo_url}
                    alt={brand.name}
                    className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-50 text-gray-500">
                    <span className="text-sm font-medium">{brand.name}</span>
                  </div>
                )}
              </div>
              <h3 className="mt-2 text-center font-medium text-gray-900 group-hover:text-blue-600 text-sm">
                {brand.name}
              </h3>
            </Link>
          ))}
        </div>
      </section>
      
      {/* Bestsellers */}
      <section className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Bestsellers</h2>
            <p className="mt-1 text-gray-600">
              Our most popular products
            </p>
          </div>
          <Link to="/products?bestsellers=true" className="text-blue-600 hover:text-blue-500 flex items-center">
            View All
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>
        <ProductGrid
          products={bestsellers}
          loading={loading}
          columns={4}
        />
      </section>
    </div>
  );
};

export default HomePage;
