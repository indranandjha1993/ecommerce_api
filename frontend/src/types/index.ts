// User types
export interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  phone_number: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  last_login: string | null;
}

export interface UserCreate {
  email: string;
  password: string;
  confirm_password: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordReset {
  token: string;
  password: string;
  confirm_password: string;
}

// Product types
export interface ProductImage {
  id: string;
  product_id: string;
  variant_id?: string;
  image_url: string;
  alt_text?: string;
  is_primary: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  parent_id?: string;
  is_active: boolean;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  website_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductAttribute {
  id: string;
  name: string;
  slug: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductAttributeValue {
  id: string;
  product_id: string;
  attribute_id: string;
  value: string;
  created_at: string;
  updated_at: string;
}

export interface ProductAttributeValueWithAttribute extends ProductAttributeValue {
  attribute: ProductAttribute;
}

export interface ProductVariantAttribute {
  attribute: ProductAttribute;
  attribute_value: ProductAttributeValue;
}

export interface ProductVariant {
  id: string;
  product_id: string;
  name?: string;
  sku?: string;
  barcode?: string;
  price?: number;
  compare_price?: number;
  cost_price?: number;
  weight?: number;
  weight_unit?: string;
  is_active: boolean;
  additional_data?: Record<string, any>;
  created_at: string;
  updated_at: string;
  variant_attributes: ProductVariantAttribute[];
  images: ProductImage[];
  inventory_quantity?: number;
}

export interface ProductListItem {
  id: string;
  name: string;
  slug: string;
  price: number;
  compare_price?: number;
  primary_image?: ProductImage;
  is_in_stock?: boolean;
  average_rating?: number;
  category?: Category;
  brand?: Brand;
}

export interface ProductList {
  items: ProductListItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  description?: string;
  short_description?: string;
  price: number;
  compare_price?: number;
  cost_price?: number;
  sku?: string;
  barcode?: string;
  weight?: number;
  weight_unit?: string;
  is_active: boolean;
  is_featured: boolean;
  is_digital: boolean;
  is_taxable: boolean;
  tax_class?: string;
  category_id?: string;
  brand_id?: string;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  additional_data?: Record<string, any>;
  created_at: string;
  updated_at: string;
  category?: Category;
  brand?: Brand;
  primary_image?: ProductImage;
  inventory_quantity?: number;
  average_rating?: number;
}

export interface ProductWithRelations extends Product {
  images: ProductImage[];
  variants: ProductVariant[];
  attribute_values: ProductAttributeValueWithAttribute[];
}

export interface ProductSearchQuery {
  query?: string;
  category_id?: string;
  brand_id?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  size?: number;
}

// Cart types
export interface CartItem {
  id: string;
  cart_id: string;
  product_id: string;
  variant_id?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  created_at: string;
  updated_at: string;
  product: ProductListItem;
  variant?: ProductVariant;
}

export interface Cart {
  id: string;
  user_id?: string;
  session_id?: string;
  status: string;
  items_count: number;
  total_amount: number;
  created_at: string;
  updated_at: string;
  items: CartItem[];
}

export interface CartItemCreate {
  product_id: string;
  variant_id?: string;
  quantity: number;
}

// Order types
export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  variant_id?: string;
  product_name: string;
  variant_name?: string;
  sku?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  created_at: string;
  updated_at: string;
}

export interface OrderAddress {
  id: string;
  order_id: string;
  address_type: 'billing' | 'shipping';
  first_name: string;
  last_name: string;
  company?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone_number?: string;
  email?: string;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: string;
  user_id?: string;
  order_number: string;
  status: string;
  payment_status: string;
  shipping_status: string;
  subtotal: number;
  shipping_cost: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  notes?: string;
  tracking_number?: string;
  shipping_method?: string;
  payment_method?: string;
  coupon_code?: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
  addresses: OrderAddress[];
}

// Review types
export interface Review {
  id: string;
  product_id: string;
  user_id: string;
  rating: number;
  title?: string;
  comment?: string;
  is_verified_purchase: boolean;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
  user_name: string;
}

// Coupon types
export interface Coupon {
  id: string;
  code: string;
  description?: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number;
  minimum_order_amount?: number;
  maximum_discount_amount?: number;
  is_active: boolean;
  starts_at?: string;
  expires_at?: string;
  usage_limit?: number;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

// Address types
export interface Address {
  id: string;
  user_id: string;
  address_type: 'billing' | 'shipping';
  is_default: boolean;
  first_name: string;
  last_name: string;
  company?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone_number?: string;
  created_at: string;
  updated_at: string;
}