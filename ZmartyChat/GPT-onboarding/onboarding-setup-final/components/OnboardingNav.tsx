import { useSwipeable } from 'react-swipeable';
import { ArrowLeft, ArrowRight } from 'lucide-react';

export default function OnboardingNav({ canGoNext, onNext, onBack }: { canGoNext: boolean; onNext: () => void; onBack: () => void }) {
  const handlers = useSwipeable({ onSwipedLeft: () => { if (canGoNext) onNext(); }, onSwipedRight: () => onBack(), trackMouse: true });
  return (
    <div {...handlers} className='flex justify-between mt-4'>
      <button onClick={onBack} className='p-2'><ArrowLeft /></button>
      <button onClick={onNext} className={`p-2 ${!canGoNext ? 'opacity-50 cursor-not-allowed' : ''}`} disabled={!canGoNext}><ArrowRight /></button>
    </div>
  );
}
