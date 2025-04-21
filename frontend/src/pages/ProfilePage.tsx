import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { updateProfile } from '../store/slices/authSlice';
import { fetchAddresses, addAddress, updateAddress, deleteAddress } from '../store/slices/addressSlice';
import { User, Address } from '../types';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import AddressForm from '../components/checkout/AddressForm';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const ProfilePage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user, loading: userLoading } = useSelector((state: RootState) => state.auth);
  const { addresses, loading: addressesLoading } = useSelector((state: RootState) => state.address);
  
  const [profileData, setProfileData] = useState<Partial<User>>({});
  const [isEditing, setIsEditing] = useState(false);
  const [isAddingAddress, setIsAddingAddress] = useState(false);
  const [editingAddressId, setEditingAddressId] = useState<string | null>(null);
  
  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone_number: user.phone_number || '',
      });
    }
    
    dispatch(fetchAddresses());
  }, [dispatch, user]);
  
  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({ ...prev, [name]: value }));
  };
  
  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await dispatch(updateProfile(profileData));
    setIsEditing(false);
  };
  
  const handleAddressSubmit = async (addressData: Partial<Address>) => {
    if (editingAddressId) {
      await dispatch(updateAddress({ id: editingAddressId, ...addressData }));
      setEditingAddressId(null);
    } else {
      await dispatch(addAddress(addressData as Address));
      setIsAddingAddress(false);
    }
  };
  
  const handleDeleteAddress = async (addressId: string) => {
    if (window.confirm('Are you sure you want to delete this address?')) {
      await dispatch(deleteAddress(addressId));
    }
  };
  
  const handleEditAddress = (address: Address) => {
    setEditingAddressId(address.id);
    setIsAddingAddress(false);
  };
  
  if (userLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  if (!user) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Profile</h2>
        <p className="text-gray-600">Unable to load user profile. Please try again later.</p>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Your Profile</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Profile Information */}
        <div className="md:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-6">Personal Information</h2>
            
            {isEditing ? (
              <form onSubmit={handleProfileSubmit}>
                <div className="space-y-4">
                  <Input
                    label="First Name"
                    name="first_name"
                    value={profileData.first_name || ''}
                    onChange={handleProfileChange}
                    fullWidth
                  />
                  
                  <Input
                    label="Last Name"
                    name="last_name"
                    value={profileData.last_name || ''}
                    onChange={handleProfileChange}
                    fullWidth
                  />
                  
                  <Input
                    label="Email"
                    value={user.email}
                    disabled
                    fullWidth
                  />
                  
                  <Input
                    label="Phone Number"
                    name="phone_number"
                    value={profileData.phone_number || ''}
                    onChange={handleProfileChange}
                    fullWidth
                  />
                </div>
                
                <div className="flex justify-end space-x-4 mt-6">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsEditing(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={userLoading}
                    disabled={userLoading}
                  >
                    Save Changes
                  </Button>
                </div>
              </form>
            ) : (
              <div>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Name</p>
                    <p className="mt-1">
                      {user.first_name || ''} {user.last_name || ''}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-gray-500">Email</p>
                    <p className="mt-1">{user.email}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-gray-500">Phone</p>
                    <p className="mt-1">{user.phone_number || 'Not provided'}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-gray-500">Member Since</p>
                    <p className="mt-1">
                      {new Date(user.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                
                <div className="mt-6">
                  <Button
                    variant="outline"
                    onClick={() => setIsEditing(true)}
                  >
                    Edit Profile
                  </Button>
                </div>
              </div>
            )}
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 mt-8">
            <h2 className="text-xl font-semibold mb-6">Account Security</h2>
            
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Password</p>
                <p className="mt-1">••••••••</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Last Login</p>
                <p className="mt-1">
                  {user.last_login
                    ? new Date(user.last_login).toLocaleString()
                    : 'Not available'}
                </p>
              </div>
            </div>
            
            <div className="mt-6">
              <Button variant="outline">Change Password</Button>
            </div>
          </div>
        </div>
        
        {/* Addresses */}
        <div className="md:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Your Addresses</h2>
              {!isAddingAddress && !editingAddressId && (
                <Button
                  variant="outline"
                  onClick={() => setIsAddingAddress(true)}
                >
                  Add New Address
                </Button>
              )}
            </div>
            
            {addressesLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : (
              <>
                {isAddingAddress && (
                  <div className="mb-8 border-b pb-8">
                    <h3 className="text-lg font-medium mb-4">Add New Address</h3>
                    <AddressForm
                      onSubmit={handleAddressSubmit}
                      showCancelButton
                      onCancel={() => setIsAddingAddress(false)}
                    />
                  </div>
                )}
                
                {editingAddressId && addresses && (
                  <div className="mb-8 border-b pb-8">
                    <h3 className="text-lg font-medium mb-4">Edit Address</h3>
                    <AddressForm
                      initialValues={addresses.find(a => a.id === editingAddressId)}
                      onSubmit={handleAddressSubmit}
                      showCancelButton
                      onCancel={() => setEditingAddressId(null)}
                    />
                  </div>
                )}
                
                {!addresses || addresses.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-4">You don't have any saved addresses yet.</p>
                    {!isAddingAddress && (
                      <Button
                        variant="primary"
                        onClick={() => setIsAddingAddress(true)}
                      >
                        Add Your First Address
                      </Button>
                    )}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-6">
                    {addresses.map((address) => (
                      <div
                        key={address.id}
                        className="border rounded-lg p-4 relative"
                      >
                        {address.is_default && (
                          <span className="absolute top-4 right-4 bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                            Default
                          </span>
                        )}
                        
                        <div className="mb-2">
                          <h4 className="font-medium">
                            {address.address_type === 'shipping' ? 'Shipping' : 'Billing'} Address
                          </h4>
                        </div>
                        
                        <div className="text-sm text-gray-600">
                          <p>{address.first_name} {address.last_name}</p>
                          <p>{address.address_line1}</p>
                          {address.address_line2 && <p>{address.address_line2}</p>}
                          <p>{address.city}, {address.state} {address.postal_code}</p>
                          <p>{address.country}</p>
                          <p>{address.phone_number}</p>
                        </div>
                        
                        <div className="mt-4 flex space-x-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditAddress(address)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={() => handleDeleteAddress(address.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;