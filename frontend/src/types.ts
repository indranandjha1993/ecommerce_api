// User types
export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

// Product types
export interface ProductImage {
  id: string;
  image_url: string;
  alt_text?: string;
  is_primary: boolean;
  sort_order: number;
}

export interface ProductSpecification {
  name: string;
  value: string;
}

export interface ProductVariant {
  id: string;
  name?: string;
  sku?: string;
  price: number;
  stock: number;
  option_type?: string;
  option_value?: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  image_url?: string;
  parent_id?: string;
  product_count?: number;
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  website?: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
}

export interface ProductReview {
  id: string;
  user: {
    id: string;
    first_name?: string;
    last_name?: string;
    email: string;
  };
  rating: number;
  title: string;
  content: string;
  created_at: string;
}

export interface ProductListItem {
  id: string;
  name: string;
  slug: string;
  sku?: string;
  price: number;
  compare_price?: number;
  short_description?: string;
  stock: number;
  is_in_stock: boolean;
  is_featured: boolean;
  average_rating?: number;
  reviews_count?: number;
  primary_image?: ProductImage;
  category?: {
    id: string;
    name: string;
    slug: string;
  };
  brand?: {
    id: string;
    name: string;
    slug: string;
  };
}

export interface Product extends ProductListItem {
  description: string;
  images: ProductImage[];
  variants?: ProductVariant[];
  specifications?: ProductSpecification[];
  categories: Category[];
  tags?: Tag[];
  related_products?: ProductListItem[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Cart types
export interface CartItem {
  id: string;
  product: ProductListItem;
  variant?: ProductVariant;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Cart {
  id: string;
  items: CartItem[];
  total_items: number;
  total_amount: number;
  created_at: string;
  updated_at: string;
}

// Address types
export interface Address {
  id: string;
  user_id: string;
  full_name: string;
  street_address: string;
  apartment?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// Order types
export interface OrderItem {
  id: string;
  product: {
    id: string;
    name: string;
    slug: string;
    primary_image?: ProductImage;
  };
  variant?: {
    id: string;
    name?: string;
    option_type?: string;
    option_value?: string;
  };
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface OrderAddress {
  full_name: string;
  street_address: string;
  apartment?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string;
}

export interface PaymentDetails {
  method: string;
  status: string;
  transaction_id?: string;
  amount: number;
  currency: string;
  payment_date?: string;
}

export interface Order {
  id: string;
  user_id: string;
  order_number: string;
  status: string;
  items: OrderItem[];
  shipping_address: OrderAddress;
  billing_address: OrderAddress;
  subtotal: number;
  shipping_fee: number;
  tax: number;
  total_amount: number;
  payment: PaymentDetails;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Notification types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ApiError {
  status: number;
  message: string;
  errors?: Record<string, string[]>;
}