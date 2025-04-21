import React, { useState } from 'react';
import { ProductImage } from '../../types';

interface ProductImageGalleryProps {
  images: ProductImage[];
}

const ProductImageGallery: React.FC<ProductImageGalleryProps> = ({ images }) => {
  const [selectedImage, setSelectedImage] = useState(images.length > 0 ? 0 : -1);
  const [isZoomed, setIsZoomed] = useState(false);
  const [zoomPosition, setZoomPosition] = useState({ x: 0, y: 0 });
  
  if (images.length === 0) {
    return (
      <div className="aspect-square bg-gray-200 rounded-lg flex items-center justify-center">
        <span className="text-gray-500">No images available</span>
      </div>
    );
  }
  
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isZoomed) return;
    
    const { left, top, width, height } = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - left) / width) * 100;
    const y = ((e.clientY - top) / height) * 100;
    
    setZoomPosition({ x, y });
  };
  
  const handleMouseLeave = () => {
    setIsZoomed(false);
  };
  
  const handleThumbnailClick = (index: number) => {
    setSelectedImage(index);
    setIsZoomed(false);
  };
  
  return (
    <div className="space-y-4">
      {/* Main image */}
      <div 
        className={`relative aspect-square overflow-hidden rounded-lg bg-gray-100 ${
          isZoomed ? 'cursor-zoom-out' : 'cursor-zoom-in'
        }`}
        onClick={() => setIsZoomed(!isZoomed)}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <img
          src={images[selectedImage].image_url}
          alt={images[selectedImage].alt_text || 'Product image'}
          className={`h-full w-full object-cover object-center transition-transform duration-300 ${
            isZoomed ? 'scale-150' : ''
          }`}
          style={
            isZoomed
              ? {
                  transformOrigin: `${zoomPosition.x}% ${zoomPosition.y}%`,
                }
              : undefined
          }
        />
      </div>
      
      {/* Thumbnails */}
      {images.length > 1 && (
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {images.map((image, index) => (
            <button
              key={index}
              className={`relative h-16 w-16 flex-shrink-0 overflow-hidden rounded-md ${
                selectedImage === index
                  ? 'ring-2 ring-blue-500 ring-offset-2'
                  : 'ring-1 ring-gray-200'
              }`}
              onClick={() => handleThumbnailClick(index)}
            >
              <img
                src={image.image_url}
                alt={image.alt_text || `Product thumbnail ${index + 1}`}
                className="h-full w-full object-cover object-center"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductImageGallery;