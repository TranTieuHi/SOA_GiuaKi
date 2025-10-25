import { useState, useEffect } from 'react';

export function useCountdown(initialTime: number = 300) {
  const [timeLeft, setTimeLeft] = useState(initialTime);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (isActive && timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [isActive, timeLeft]);

  const start = (time?: number) => {
    if (time) setTimeLeft(time);
    setIsActive(true);
  };

  const reset = (time: number = initialTime) => {
    setTimeLeft(time);
    setIsActive(false);
  };

  const stop = () => {
    setIsActive(false);
  };

  return {
    timeLeft,
    isActive,
    isExpired: timeLeft === 0,
    start,
    reset,
    stop
  };
}