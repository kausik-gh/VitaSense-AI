import React from 'react';

export const VitalSignsIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12,2A10,10,0,1,0,22,12,10,10,0,0,0,12,2Zm5.5,11h-3l-1.5,4L10,8,8.5,13h-3a0.5,0.5,0,0,1,0-1h3l1.5-4L13,17l1.5-5h3a0.5,0.5,0,0,1,0,1Z" />
  </svg>
);

export const HealthSafetyIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12,2L4.5,5V11C4.5,15.55 7.67,19.74 12,21C16.33,19.74 19.5,15.55 19.5,11V5L12,2M12,19.33C8.83,18.17 6.5,14.77 6.5,11.5V6.63L12,4.43L17.5,6.63V11.5C17.5,14.77 15.17,18.17 12,19.33M11,10V7H13V10H16V12H13V15H11V12H8V10H11Z" />
  </svg>
);

export const ShieldCheckIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,21C12,21 8.52,18.42 8.52,11V6.3L12,4.76L15.48,6.3V11C15.48,18.42 12,21 12,21M10.59,15.41L16.24,9.76L17.66,11.17L10.59,18.24L6.34,14L7.75,12.59L10.59,15.41Z" />
  </svg>
);
