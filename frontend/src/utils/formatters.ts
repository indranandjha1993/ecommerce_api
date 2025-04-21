/**
 * Format a price with currency symbol
 * @param price - The price to format
 * @param currency - The currency code (default: USD)
 * @returns Formatted price string
 */
export const formatPrice = (price: number | undefined, currency: string = 'USD'): string => {
  if (price === undefined) return '';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(price);
};

/**
 * Format a date string
 * @param dateString - ISO date string
 * @param options - Intl.DateTimeFormatOptions
 * @returns Formatted date string
 */
export const formatDate = (
  dateString: string | undefined,
  options: Intl.DateTimeFormatOptions = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }
): string => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', options).format(date);
};

/**
 * Calculate discount percentage
 * @param price - Current price
 * @param comparePrice - Original price
 * @returns Discount percentage or null if no discount
 */
export const calculateDiscount = (
  price: number | undefined, 
  comparePrice: number | undefined
): number | null => {
  if (!price || !comparePrice || comparePrice <= price) return null;
  
  const discount = ((comparePrice - price) / comparePrice) * 100;
  return Math.round(discount);
};

/**
 * Truncate text to a specified length
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns Truncated text with ellipsis if needed
 */
export const truncateText = (text: string | undefined, maxLength: number): string => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Generate initials from a name
 * @param firstName - First name
 * @param lastName - Last name
 * @returns Initials (1-2 characters)
 */
export const getInitials = (firstName: string | null, lastName: string | null): string => {
  let initials = '';
  
  if (firstName) {
    initials += firstName.charAt(0).toUpperCase();
  }
  
  if (lastName) {
    initials += lastName.charAt(0).toUpperCase();
  }
  
  return initials || '?';
};

/**
 * Format a phone number
 * @param phone - Phone number string
 * @returns Formatted phone number
 */
export const formatPhoneNumber = (phone: string | null): string => {
  if (!phone) return '';
  
  // Remove all non-numeric characters
  const cleaned = phone.replace(/\D/g, '');
  
  // Format based on length
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  
  return phone;
};