import { z } from 'zod';

// User registration schema
export const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirm_password: z.string(),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  phone_number: z.string().optional(),
}).refine(data => data.password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
});

// Login schema
export const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

// Password reset request schema
export const passwordResetRequestSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

// Password reset schema
export const passwordResetSchema = z.object({
  token: z.string(),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirm_password: z.string(),
}).refine(data => data.password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
});

// Address schema
export const addressSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  company: z.string().optional(),
  address_line1: z.string().min(1, 'Address is required'),
  address_line2: z.string().optional(),
  city: z.string().min(1, 'City is required'),
  state: z.string().min(1, 'State is required'),
  postal_code: z.string().min(1, 'Postal code is required'),
  country: z.string().min(1, 'Country is required'),
  phone_number: z.string().optional(),
  is_default: z.boolean().optional(),
});

// Checkout schema
export const checkoutSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Please enter a valid email address'),
  phone_number: z.string().min(1, 'Phone number is required'),
  address_line1: z.string().min(1, 'Address is required'),
  address_line2: z.string().optional(),
  city: z.string().min(1, 'City is required'),
  state: z.string().min(1, 'State is required'),
  postal_code: z.string().min(1, 'Postal code is required'),
  country: z.string().min(1, 'Country is required'),
  shipping_method: z.string().min(1, 'Shipping method is required'),
  payment_method: z.string().min(1, 'Payment method is required'),
  card_number: z.string().optional()
    .refine(val => !val || val.replace(/\s/g, '').length === 16, {
      message: 'Card number must be 16 digits',
    }),
  card_expiry: z.string().optional()
    .refine(val => !val || /^\d{2}\/\d{2}$/.test(val), {
      message: 'Expiry date must be in MM/YY format',
    }),
  card_cvc: z.string().optional()
    .refine(val => !val || /^\d{3,4}$/.test(val), {
      message: 'CVC must be 3 or 4 digits',
    }),
  save_payment_method: z.boolean().optional(),
}).refine(
  data => {
    if (data.payment_method === 'credit_card') {
      return !!data.card_number && !!data.card_expiry && !!data.card_cvc;
    }
    return true;
  },
  {
    message: 'Credit card details are required',
    path: ['card_number'],
  }
);

// Contact form schema
export const contactFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Please enter a valid email address'),
  subject: z.string().min(1, 'Subject is required'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
});

// Review schema
export const reviewSchema = z.object({
  rating: z.number().min(1).max(5),
  title: z.string().min(1, 'Title is required'),
  comment: z.string().min(10, 'Comment must be at least 10 characters'),
});