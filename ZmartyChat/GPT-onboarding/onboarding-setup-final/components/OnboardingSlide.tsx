import { ReactNode } from 'react';
export default function OnboardingSlide({ children }: { children: ReactNode }) {
  return <div className='flex justify-center items-center min-h-screen bg-gray-100'><div className='bg-white rounded-xl shadow-md w-full max-w-md p-6'>{children}</div></div>;
}
