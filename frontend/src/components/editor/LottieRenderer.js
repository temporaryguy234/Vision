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
