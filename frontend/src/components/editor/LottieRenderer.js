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
    const backendBase = process.env.REACT_APP_BACKEND_URL || window.location.origin;

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
        } else {
          let resolvedUrl = sourceUrl;
          if (resolvedUrl.startsWith('/uploads/')) {
            // Use the new direct Lottie endpoint for uploads
            const filePath = resolvedUrl.replace('/uploads/', '');
            const lottieUrl = `${backendBase}/api/lottie/${filePath}`;
            const response = await fetch(lottieUrl);
            if (!response.ok) throw new Error(`Failed to load Lottie file: ${response.status}`);
            data = await response.json();
          } else {
            // For external URLs, try direct fetch first, then proxy
            try {
              const response = await fetch(resolvedUrl);
              if (!response.ok) throw new Error(`HTTP ${response.status}`);
              data = await response.json();
            } catch (error) {
              console.warn('Direct fetch failed, trying proxy:', error.message);
              // Fallback to proxy for external URLs
              const proxyUrl = `${backendBase}/api/proxy/fetch-json?url=${encodeURIComponent(resolvedUrl)}`;
              const proxyResp = await fetch(proxyUrl);
              if (!proxyResp.ok) throw new Error(`Failed to load animation via proxy: ${proxyResp.status}`);
              data = await proxyResp.json();
            }
          }
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
        className={`inline-block ${className} ${isSelected ? 'ring-2 ring-orange-500 rounded' : ''}`}
        onClick={onClick}
        onMouseDown={onDragStart}
        style={{ 
          width: '100%',
          height: '100%',
          minWidth: '150px',
          minHeight: '150px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f8f9fa',
          border: '2px solid #e9ecef',
          borderRadius: '8px',
          position: 'relative'
        }}
      >
        {/* Enhanced fallback with animation preview */}
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-2 relative">
            <div className="absolute inset-0 border-4 border-orange-200 rounded-full animate-spin"></div>
            <div className="absolute inset-2 border-4 border-orange-500 rounded-full animate-pulse"></div>
          </div>
          <div className="text-sm font-medium text-gray-700">Motion Graphic</div>
          <div className="text-xs text-gray-500 mt-1">
            {animationData ? `${animationData.w || 0}×${animationData.h || 0}` : 'Preview'}
          </div>
          {animationData?.layers && (
            <div className="text-xs text-gray-400 mt-1">
              {animationData.layers.length} layers
            </div>
          )}
          {error && (
            <div className="text-xs text-red-500 mt-2 px-2 py-1 bg-red-50 rounded">
              {error}
            </div>
          )}
        </div>
        
        {/* Play button overlay */}
        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 rounded-lg">
            <div className="w-12 h-12 bg-white bg-opacity-90 rounded-full flex items-center justify-center shadow-lg">
              <div className="w-0 h-0 border-l-4 border-l-orange-500 border-t-3 border-t-transparent border-b-3 border-b-transparent ml-1"></div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div 
      className={`inline-block ${className} ${isSelected ? 'ring-2 ring-orange-500 rounded' : ''}`}
      onClick={onClick}
      onMouseDown={onDragStart}
      style={{ 
        width: '100%', 
        height: '100%',
        minWidth: '150px',
        minHeight: '150px'
      }}
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

// --- Preview helpers ---
export async function renderLottiePreview({ animationData, width = 400, height = 400, durationSeconds = 2.5, fps = 30 }) {
  // Render frames to canvas and return a WebM Blob and a PNG Blob of the last frame
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // Use an offscreen <lottie-player> via lottie-web if needed; here we draw frames by time using Lottie's API via lottie-web
  // lottie-react does not expose frame-stepping; for recording we dynamically import lottie-web
  const lottieWeb = await import('lottie-web');
  const container = document.createElement('div');
  const anim = lottieWeb.loadAnimation({
    container,
    renderer: 'canvas',
    loop: false,
    autoplay: false,
    animationData
  });

  await new Promise((resolve) => {
    anim.addEventListener('DOMLoaded', () => resolve());
  });

  const totalFrames = Math.min(Math.floor(durationSeconds * fps), Math.floor(anim.getDuration(true)));

  const stream = canvas.captureStream(fps);
  const recorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' });
  const chunks = [];
  recorder.ondataavailable = (e) => { if (e.data && e.data.size) chunks.push(e.data); };
  const stopped = new Promise((resolve) => recorder.onstop = resolve);
  recorder.start();

  // Draw frames
  for (let i = 0; i < totalFrames; i++) {
    anim.goToAndStop(i, true);
    // Draw the animation's canvas onto our canvas
    const sourceCanvas = container.querySelector('canvas');
    if (sourceCanvas) {
      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(sourceCanvas, 0, 0, width, height);
    }
    await new Promise(r => setTimeout(r, 1000 / fps));
  }

  recorder.stop();
  await stopped;

  const webmBlob = new Blob(chunks, { type: 'video/webm' });
  const pngBlob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));

  anim.destroy();

  return { webmBlob, pngBlob };
}
