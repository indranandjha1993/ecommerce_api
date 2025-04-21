import React from 'react';
import { ProductVariant } from '../../types';
import Badge from '../ui/Badge';
import { formatPrice } from '../../utils/formatters';

interface ProductVariantSelectorProps {
  variants: ProductVariant[];
  selectedVariantId: string | null;
  onChange: (variantId: string) => void;
}

const ProductVariantSelector: React.FC<ProductVariantSelectorProps> = ({
  variants,
  selectedVariantId,
  onChange,
}) => {
  // Group variants by option type (e.g., "Color", "Size")
  const getOptionTypes = () => {
    const optionTypes = new Set<string>();
    variants.forEach((variant) => {
      if (variant.option_type) {
        optionTypes.add(variant.option_type);
      }
    });
    return Array.from(optionTypes);
  };

  const optionTypes = getOptionTypes();

  // If no option types, just show a simple list of variants
  if (optionTypes.length === 0) {
    return (
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Variants
        </label>
        <div className="grid grid-cols-2 gap-2">
          {variants.map((variant) => (
            <button
              key={variant.id}
              type="button"
              className={`relative border rounded-md py-2 px-4 flex items-center justify-between focus:outline-none ${
                selectedVariantId === variant.id
                  ? 'border-blue-500 ring-2 ring-blue-500'
                  : 'border-gray-300 hover:border-gray-400'
              } ${!variant.stock ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => variant.stock && onChange(variant.id)}
              disabled={!variant.stock}
            >
              <span className="text-sm font-medium text-gray-900">
                {variant.name || 'Variant'}
              </span>
              <span className="text-sm text-gray-500">
                {formatPrice(variant.price)}
              </span>
              {!variant.stock && (
                <Badge variant="danger" className="absolute top-0 right-0 transform translate-x-1/3 -translate-y-1/3">
                  Out of stock
                </Badge>
              )}
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Otherwise, organize by option type
  return (
    <div className="space-y-4">
      {optionTypes.map((optionType) => {
        // Get unique option values for this type
        const optionValues = Array.from(
          new Set(
            variants
              .filter((v) => v.option_type === optionType)
              .map((v) => v.option_value)
          )
        );

        // Find the selected variant's option value for this type
        const selectedVariant = variants.find((v) => v.id === selectedVariantId);
        const selectedValue = selectedVariant?.option_type === optionType
          ? selectedVariant.option_value
          : null;

        return (
          <div key={optionType}>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {optionType}
            </label>
            <div className="flex flex-wrap gap-2">
              {optionValues.map((value) => {
                // Find a variant with this option type and value
                const variantWithValue = variants.find(
                  (v) => v.option_type === optionType && v.option_value === value
                );
                
                // Check if this option is available (has stock)
                const isAvailable = !!variantWithValue?.stock;
                
                // Determine if this option should be selected
                const isSelected = selectedValue === value;
                
                // Find the variant ID to use when this option is selected
                const variantToSelect = variants.find(
                  (v) => 
                    v.option_type === optionType && 
                    v.option_value === value && 
                    v.stock > 0
                );
                
                return (
                  <button
                    key={value}
                    type="button"
                    className={`relative border rounded-md py-2 px-4 focus:outline-none ${
                      isSelected
                        ? 'border-blue-500 ring-2 ring-blue-500'
                        : 'border-gray-300 hover:border-gray-400'
                    } ${!isAvailable ? 'opacity-50 cursor-not-allowed' : ''}`}
                    onClick={() => isAvailable && variantToSelect && onChange(variantToSelect.id)}
                    disabled={!isAvailable}
                  >
                    <span className="text-sm font-medium text-gray-900">
                      {value}
                    </span>
                    {!isAvailable && (
                      <span className="absolute inset-0 flex items-center justify-center bg-gray-100 bg-opacity-50 text-xs text-gray-500">
                        Out of stock
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ProductVariantSelector;