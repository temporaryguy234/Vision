import React, { useRef, useEffect } from 'react';
import Lottie from 'lottie-react';

const LottieRenderer = ({ 
  sourceUrl, 
  loop = true, 
  autoplay = true, 
  speed = 1.0,
  isSelected,
  isPlaying,
  onClick,
  onDragStart,
  className = "",
  animationData: externalAnimationData
}) => {
  const lottieRef = useRef(null);

  // Control playback based on isPlaying prop
  useEffect(() => {
    if (lottieRef.current) {
      if (isPlaying && autoplay) {
        lottieRef.current.play();
      } else {
        lottieRef.current.pause();
      }
    }
  }, [isPlaying, autoplay]);

  // Set animation speed
  useEffect(() => {
    if (lottieRef.current) {
      lottieRef.current.setSpeed(speed);
    }
  }, [speed]);

  // Handle loading state and errors
  const [animationData, setAnimationData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  useEffect(() => {
    const backendBase = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    // If external data is provided, use it directly
    if (externalAnimationData) {
      setAnimationData(externalAnimationData);
      setError(null);
      setLoading(false);
      return;
    }

    if (!sourceUrl) {
      setError('No source provided');
      setLoading(false);
      return;
    }

    const loadAnimation = async () => {
      try {
        setLoading(true);
        setError(null);

        let data;

        if (sourceUrl.startsWith('embedded://')) {
          const animationId = sourceUrl.replace('embedded://', '');
          const response = await fetch(`${backendBase}/api/lottiefiles/animation/${animationId}/data`);
          if (!response.ok) throw new Error(`Failed to load embedded animation: ${response.status}`);
          data = await response.json();
        } else if (sourceUrl.startsWith('/uploads/')) {
          const response = await fetch(`${backendBase}${sourceUrl}`);
          if (!response.ok) throw new Error(`Failed to load animation: ${response.status}`);
          data = await response.json();
        } else {
          const response = await fetch(sourceUrl);
          if (!response.ok) throw new Error(`Failed to load animation: ${response.status}`);
          data = await response.json();
        }

        setAnimationData(data);
      } catch (err) {
        console.error('Error loading Lottie animation:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadAnimation();
  }, [sourceUrl, externalAnimationData]);

  if (loading) {
    return (
      <div 
        className={`w-24 h-24 border-2 border-dashed border-gray-300 bg-gray-100 flex items-center justify-center rounded ${className} ${isSelected ? 'ring-2 ring-orange-500' : ''}`}
        onClick={onClick}
        onMouseDown={onDragStart}
      >
        <div className="animate-spin w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (error || !animationData) {
    return (
      <div 
        className={`w-24 h-24 border-2 border-dashed border-red-300 bg-red-50 flex flex-col items-center justify-center rounded ${className} ${isSelected ? 'ring-2 ring-orange-500' : ''}`}
        onClick={onClick}
        onMouseDown={onDragStart}
      >
        <span className="text-red-500 text-xs text-center">
          Lottie Error
        </span>
        <span className="text-red-400 text-xs text-center mt-1">
          {error || 'Failed to load'}
        </span>
      </div>
    );
  }

  return (
    <div 
      className={`inline-block ${className} ${isSelected ? 'ring-2 ring-orange-500 rounded' : ''}`}
      onClick={onClick}
      onMouseDown={onDragStart}
      style={{ width: '96px', height: '96px' }} // Fixed size for now
    >
      <Lottie
        lottieRef={lottieRef}
        animationData={animationData}
        loop={loop}
        autoplay={autoplay && isPlaying}
        style={{ 
          width: '100%', 
          height: '100%',
        }}
        rendererSettings={{
          preserveAspectRatio: 'xMidYMid meet'
        }}
      />
    </div>
  );
};

export default LottieRenderer;