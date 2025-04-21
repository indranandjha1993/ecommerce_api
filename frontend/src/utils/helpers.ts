/**
 * Collection of helper functions for the e-commerce application
 */

/**
 * Truncates a string to a specified length and adds ellipsis if needed
 * @param str - The string to truncate
 * @param maxLength - Maximum length of the string
 * @returns Truncated string with ellipsis if needed
 */
export const truncateString = (str: string, maxLength: number): string => {
  if (!str) return '';
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + '...';
};

/**
 * Generates a random string ID
 * @param length - Length of the ID
 * @returns Random string ID
 */
export const generateId = (length: number = 8): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

/**
 * Debounces a function call
 * @param func - Function to debounce
 * @param wait - Wait time in milliseconds
 * @returns Debounced function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;
  
  return function(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttles a function call
 * @param func - Function to throttle
 * @param limit - Limit time in milliseconds
 * @returns Throttled function
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean = false;
  
  return function(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
};

/**
 * Formats a price with currency symbol
 * @param price - Price to format
 * @param currency - Currency code (default: USD)
 * @param locale - Locale for formatting (default: en-US)
 * @returns Formatted price string
 */
export const formatPrice = (
  price: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(price);
};

/**
 * Calculates discount percentage
 * @param originalPrice - Original price
 * @param discountedPrice - Discounted price
 * @returns Discount percentage
 */
export const calculateDiscountPercentage = (
  originalPrice: number,
  discountedPrice: number
): number => {
  if (originalPrice <= 0) return 0;
  const discount = originalPrice - discountedPrice;
  return Math.round((discount / originalPrice) * 100);
};

/**
 * Formats a date string
 * @param dateString - Date string to format
 * @param options - Intl.DateTimeFormatOptions
 * @param locale - Locale for formatting (default: en-US)
 * @returns Formatted date string
 */
export const formatDate = (
  dateString: string,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  },
  locale: string = 'en-US'
): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat(locale, options).format(date);
};

/**
 * Formats a date relative to now (e.g., "2 days ago")
 * @param dateString - Date string to format
 * @returns Relative time string
 */
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
  
  if (diffInSeconds < 60) {
    return rtf.format(-diffInSeconds, 'second');
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return rtf.format(-diffInMinutes, 'minute');
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return rtf.format(-diffInHours, 'hour');
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) {
    return rtf.format(-diffInDays, 'day');
  }
  
  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return rtf.format(-diffInMonths, 'month');
  }
  
  const diffInYears = Math.floor(diffInMonths / 12);
  return rtf.format(-diffInYears, 'year');
};

/**
 * Slugifies a string (converts to lowercase, replaces spaces with hyphens)
 * @param str - String to slugify
 * @returns Slugified string
 */
export const slugify = (str: string): string => {
  return str
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

/**
 * Extracts query parameters from a URL
 * @param url - URL to extract query parameters from
 * @returns Object with query parameters
 */
export const getQueryParams = (url: string): Record<string, string> => {
  const params: Record<string, string> = {};
  const queryString = url.split('?')[1];
  
  if (!queryString) return params;
  
  const pairs = queryString.split('&');
  for (const pair of pairs) {
    const [key, value] = pair.split('=');
    params[decodeURIComponent(key)] = decodeURIComponent(value || '');
  }
  
  return params;
};

/**
 * Builds a URL with query parameters
 * @param baseUrl - Base URL
 * @param params - Query parameters
 * @returns URL with query parameters
 */
export const buildUrl = (baseUrl: string, params: Record<string, string | number | boolean>): string => {
  const url = new URL(baseUrl);
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.append(key, String(value));
    }
  });
  
  return url.toString();
};

/**
 * Validates an email address
 * @param email - Email address to validate
 * @returns Whether the email is valid
 */
export const isValidEmail = (email: string): boolean => {
  const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return re.test(email);
};

/**
 * Validates a password (min 8 chars, at least one letter and one number)
 * @param password - Password to validate
 * @returns Whether the password is valid
 */
export const isValidPassword = (password: string): boolean => {
  const re = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
  return re.test(password);
};

/**
 * Validates a phone number
 * @param phone - Phone number to validate
 * @returns Whether the phone number is valid
 */
export const isValidPhone = (phone: string): boolean => {
  const re = /^\+?[1-9]\d{9,14}$/;
  return re.test(phone);
};

/**
 * Gets the file extension from a filename
 * @param filename - Filename to get extension from
 * @returns File extension
 */
export const getFileExtension = (filename: string): string => {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
};

/**
 * Checks if a file is an image
 * @param filename - Filename to check
 * @returns Whether the file is an image
 */
export const isImageFile = (filename: string): boolean => {
  const ext = getFileExtension(filename).toLowerCase();
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext);
};

/**
 * Formats a file size
 * @param bytes - File size in bytes
 * @param decimals - Number of decimal places
 * @returns Formatted file size
 */
export const formatFileSize = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Checks if the user is on a mobile device
 * @returns Whether the user is on a mobile device
 */
export const isMobileDevice = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

/**
 * Gets the browser name
 * @returns Browser name
 */
export const getBrowserName = (): string => {
  const userAgent = navigator.userAgent;
  
  if (userAgent.indexOf('Firefox') > -1) return 'Firefox';
  if (userAgent.indexOf('Opera') > -1 || userAgent.indexOf('OPR') > -1) return 'Opera';
  if (userAgent.indexOf('Trident') > -1) return 'Internet Explorer';
  if (userAgent.indexOf('Edge') > -1) return 'Edge';
  if (userAgent.indexOf('Chrome') > -1) return 'Chrome';
  if (userAgent.indexOf('Safari') > -1) return 'Safari';
  
  return 'Unknown';
};

/**
 * Copies text to clipboard
 * @param text - Text to copy
 * @returns Promise that resolves when text is copied
 */
export const copyToClipboard = async (text: string): Promise<void> => {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text);
  }
  
  // Fallback for older browsers
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  
  try {
    document.execCommand('copy');
  } catch (err) {
    console.error('Failed to copy text: ', err);
  }
  
  document.body.removeChild(textArea);
};

/**
 * Scrolls to an element
 * @param elementId - ID of the element to scroll to
 * @param offset - Offset from the top
 * @param behavior - Scroll behavior
 */
export const scrollToElement = (
  elementId: string,
  offset: number = 0,
  behavior: ScrollBehavior = 'smooth'
): void => {
  const element = document.getElementById(elementId);
  if (!element) return;
  
  const elementPosition = element.getBoundingClientRect().top;
  const offsetPosition = elementPosition + window.pageYOffset - offset;
  
  window.scrollTo({
    top: offsetPosition,
    behavior,
  });
};

/**
 * Gets a random item from an array
 * @param array - Array to get random item from
 * @returns Random item from array
 */
export const getRandomItem = <T>(array: T[]): T => {
  return array[Math.floor(Math.random() * array.length)];
};

/**
 * Shuffles an array
 * @param array - Array to shuffle
 * @returns Shuffled array
 */
export const shuffleArray = <T>(array: T[]): T[] => {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
};

/**
 * Groups an array of objects by a key
 * @param array - Array to group
 * @param key - Key to group by
 * @returns Grouped object
 */
export const groupBy = <T>(array: T[], key: keyof T): Record<string, T[]> => {
  return array.reduce((result, item) => {
    const groupKey = String(item[key]);
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {} as Record<string, T[]>);
};

/**
 * Sorts an array of objects by a key
 * @param array - Array to sort
 * @param key - Key to sort by
 * @param direction - Sort direction
 * @returns Sorted array
 */
export const sortBy = <T>(
  array: T[],
  key: keyof T,
  direction: 'asc' | 'desc' = 'asc'
): T[] => {
  return [...array].sort((a, b) => {
    if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
    if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
    return 0;
  });
};

/**
 * Filters an array of objects by a key and value
 * @param array - Array to filter
 * @param key - Key to filter by
 * @param value - Value to filter by
 * @returns Filtered array
 */
export const filterBy = <T>(array: T[], key: keyof T, value: any): T[] => {
  return array.filter(item => item[key] === value);
};

/**
 * Removes duplicate items from an array
 * @param array - Array to remove duplicates from
 * @param key - Key to check for duplicates (for objects)
 * @returns Array without duplicates
 */
export const removeDuplicates = <T>(array: T[], key?: keyof T): T[] => {
  if (key) {
    const seen = new Set();
    return array.filter(item => {
      const value = item[key];
      if (seen.has(value)) return false;
      seen.add(value);
      return true;
    });
  }
  
  return [...new Set(array)];
};

/**
 * Checks if an object is empty
 * @param obj - Object to check
 * @returns Whether the object is empty
 */
export const isEmptyObject = (obj: Record<string, any>): boolean => {
  return Object.keys(obj).length === 0;
};

/**
 * Deep clones an object
 * @param obj - Object to clone
 * @returns Cloned object
 */
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Merges two objects deeply
 * @param target - Target object
 * @param source - Source object
 * @returns Merged object
 */
export const deepMerge = <T extends Record<string, any>, U extends Record<string, any>>(
  target: T,
  source: U
): T & U => {
  const output = { ...target } as T & U;
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!(key in target)) {
          Object.assign(output, { [key]: source[key] });
        } else {
          output[key] = deepMerge(target[key], source[key]);
        }
      } else {
        Object.assign(output, { [key]: source[key] });
      }
    });
  }
  
  return output;
};

/**
 * Checks if a value is an object
 * @param item - Value to check
 * @returns Whether the value is an object
 */
export const isObject = (item: any): boolean => {
  return item && typeof item === 'object' && !Array.isArray(item);
};

/**
 * Gets a nested property from an object using a path
 * @param obj - Object to get property from
 * @param path - Path to property (e.g., 'user.address.city')
 * @param defaultValue - Default value if property doesn't exist
 * @returns Property value or default value
 */
export const getNestedProperty = <T>(
  obj: Record<string, any>,
  path: string,
  defaultValue: T
): T => {
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    if (result === undefined || result === null) {
      return defaultValue;
    }
    result = result[key];
  }
  
  return result === undefined ? defaultValue : result;
};

/**
 * Sets a nested property in an object using a path
 * @param obj - Object to set property in
 * @param path - Path to property (e.g., 'user.address.city')
 * @param value - Value to set
 * @returns Updated object
 */
export const setNestedProperty = <T>(
  obj: Record<string, any>,
  path: string,
  value: T
): Record<string, any> => {
  const keys = path.split('.');
  const lastKey = keys.pop()!;
  const result = { ...obj };
  
  let current = result;
  for (const key of keys) {
    if (!(key in current)) {
      current[key] = {};
    }
    current = current[key];
  }
  
  current[lastKey] = value;
  return result;
};

/**
 * Converts a string to title case
 * @param str - String to convert
 * @returns Title case string
 */
export const toTitleCase = (str: string): string => {
  return str.replace(
    /\w\S*/g,
    txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};

/**
 * Converts a string to camel case
 * @param str - String to convert
 * @returns Camel case string
 */
export const toCamelCase = (str: string): string => {
  return str
    .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => {
      return index === 0 ? word.toLowerCase() : word.toUpperCase();
    })
    .replace(/\s+/g, '');
};

/**
 * Converts a string to snake case
 * @param str - String to convert
 * @returns Snake case string
 */
export const toSnakeCase = (str: string): string => {
  return str
    .replace(/\s+/g, '_')
    .replace(/([A-Z])/g, '_$1')
    .toLowerCase()
    .replace(/^_/, '');
};

/**
 * Converts a string to kebab case
 * @param str - String to convert
 * @returns Kebab case string
 */
export const toKebabCase = (str: string): string => {
  return str
    .replace(/\s+/g, '-')
    .replace(/([A-Z])/g, '-$1')
    .toLowerCase()
    .replace(/^-/, '');
};