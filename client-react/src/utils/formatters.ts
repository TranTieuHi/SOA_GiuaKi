export const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export const formatCurrency = (amount: number): string => {
  return amount.toLocaleString('vi-VN');
};

export const formatEmail = (email: string): string => {
  if (!email) return '';
  const [localPart, domain] = email.split('@');
  if (localPart.length <= 3) return email;
  
  const visiblePart = localPart.slice(0, 3);
  const hiddenPart = '*'.repeat(localPart.length - 3);
  return `${visiblePart}${hiddenPart}@${domain}`;
};