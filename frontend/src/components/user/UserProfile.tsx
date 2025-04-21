import React, { useState } from 'react';
import { twMerge } from 'tailwind-merge';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Alert from '../ui/Alert';
import { User } from '../../types';

export interface UserProfileProps {
  user: User;
  onUpdateProfile: (data: Partial<User>) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

const UserProfile: React.FC<UserProfileProps> = ({
  user,
  onUpdateProfile,
  isLoading = false,
  error = null,
  className,
}) => {
  const [name, setName] = useState(user.name || '');
  const [email, setEmail] = useState(user.email || '');
  const [phone, setPhone] = useState(user.phone || '');
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSuccess(null);

    try {
      await onUpdateProfile({
        name,
        email,
        phone,
      });
      setSuccess('Profile updated successfully');
      setIsEditing(false);
    } catch (err) {
      setFormError('Failed to update profile');
      console.error('Profile update error:', err);
    }
  };

  // Cancel editing
  const handleCancel = () => {
    setName(user.name || '');
    setEmail(user.email || '');
    setPhone(user.phone || '');
    setIsEditing(false);
    setFormError(null);
  };

  return (
    <Card 
      className={twMerge('w-full', className)}
      padding="lg"
      shadow="sm"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-neutral-900">Profile Information</h2>
        {!isEditing && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsEditing(true)}
          >
            Edit Profile
          </Button>
        )}
      </div>

      {(error || formError) && (
        <Alert 
          variant="error" 
          title="Error" 
          className="mb-4"
          onClose={() => setFormError(null)}
        >
          {error || formError}
        </Alert>
      )}

      {success && (
        <Alert 
          variant="success" 
          title="Success" 
          className="mb-4"
          onClose={() => setSuccess(null)}
        >
          {success}
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="w-full md:w-1/3">
            <div className="flex flex-col items-center">
              <div className="relative mb-4">
                <div className="h-32 w-32 rounded-full bg-neutral-200 flex items-center justify-center overflow-hidden">
                  {user.avatar ? (
                    <img 
                      src={user.avatar} 
                      alt={user.name || 'User'} 
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <svg 
                      className="h-16 w-16 text-neutral-400" 
                      fill="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                    </svg>
                  )}
                </div>
                {isEditing && (
                  <Button
                    variant="primary"
                    size="sm"
                    className="absolute bottom-0 right-0 rounded-full h-8 w-8 p-0"
                    type="button"
                  >
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" 
                      className="h-4 w-4" 
                      viewBox="0 0 20 20" 
                      fill="currentColor"
                    >
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </Button>
                )}
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-neutral-900">{user.name}</h3>
                <p className="text-sm text-neutral-500">Member since {new Date(user.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          <div className="w-full md:w-2/3">
            <div className="space-y-4">
              <Input
                label="Full Name"
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={!isEditing || isLoading}
                required
              />

              <Input
                label="Email Address"
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={!isEditing || isLoading}
                required
              />

              <Input
                label="Phone Number"
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                disabled={!isEditing || isLoading}
              />

              {isEditing && (
                <div className="flex justify-end space-x-3 pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="md"
                    onClick={handleCancel}
                    disabled={isLoading}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    size="md"
                    isLoading={isLoading}
                    loadingText="Saving..."
                  >
                    Save Changes
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </form>
    </Card>
  );
};

export default UserProfile;