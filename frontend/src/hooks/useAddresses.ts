import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  fetchAddresses, 
  fetchAddressById, 
  addAddress, 
  updateAddress, 
  deleteAddress,
  setDefaultAddress,
  clearError,
  selectAddresses,
  selectAddressLoading,
  selectAddressError
} from '../store/slices/addressSlice';
import { AppDispatch } from '../store';
import { Address } from '../types';

export const useAddresses = () => {
  const dispatch = useDispatch<AppDispatch>();
  
  const addresses = useSelector(selectAddresses);
  const loading = useSelector(selectAddressLoading);
  const error = useSelector(selectAddressError);
  
  const getAddresses = useCallback(() => {
    return dispatch(fetchAddresses());
  }, [dispatch]);
  
  const getAddressById = useCallback((id: string) => {
    return dispatch(fetchAddressById(id));
  }, [dispatch]);
  
  const createAddress = useCallback((addressData: Partial<Address>) => {
    return dispatch(addAddress(addressData));
  }, [dispatch]);
  
  const editAddress = useCallback((id: string, addressData: Partial<Address>) => {
    return dispatch(updateAddress({ id, ...addressData }));
  }, [dispatch]);
  
  const removeAddress = useCallback((id: string) => {
    return dispatch(deleteAddress(id));
  }, [dispatch]);
  
  const makeDefaultAddress = useCallback((id: string) => {
    return dispatch(setDefaultAddress(id));
  }, [dispatch]);
  
  const resetError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);
  
  return {
    addresses,
    loading,
    error,
    fetchAddresses: getAddresses,
    fetchAddressById: getAddressById,
    addAddress: createAddress,
    updateAddress: editAddress,
    deleteAddress: removeAddress,
    setDefaultAddress: makeDefaultAddress,
    clearError: resetError
  };
};