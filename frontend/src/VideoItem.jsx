import { useEffect, useRef, useState } from "react";
import { Button } from "./components/ui/button";

const API_URL = "http://localhost:8000"

export default function VideoItem({ video, index, total }) {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    const element = videoRef.current;

    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          element
            .play()
            .then(() => setIsPlaying(true))
            .catch(() => {});
        } else {
          element.pause();
          setIsPlaying(false)
        }
      },
      {
        threshold: 0.7,
      },
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, []);

  const togglePlay = () => {
    const videoElement = videoRef.current;
    if (!videoElement) return;

    if (videoElement.paused) {
      videoElement.play();
      setIsPlaying(true);
    } else {
      videoElement.pause();
      setIsPlaying(false);
    }
  };

  async function toggleFullScreen() {
    const videoElement = videoRef.current;

    if (!videoElement) return;

    if (!document.fullscreenElement) {
      await videoElement.requestFullscreen();
    } else {
      await document.exitFullscreen();
    }
  }

  return (
    <section className="relative flex h-screen w-full snap-start items-center justify-center">
      <video
        ref={videoRef}
        src={`${API_URL}${video.url}`}
        className="h-full w-full object-contain"
        muted
        loop
        playsInline
        tabIndex={0}
        onClick={togglePlay}
        onKeyDown={(event) => {
          if (event.code === "Space") {
            event.preventDefault()
            togglePlay()
          }
        }}
      />

      <div className="absolute bottom-6 left-6 rounded-full bg-black/50 px-3 py-1 text-sm text-white">
        <p>
          {index + 1} / {total}
        </p>
      </div>

      <div className="absolute bottom-6 right-6 flex flex-col gap-3">
        <Button onClick={togglePlay} className="rounded-full">
          {isPlaying ? "Pause": "Play"}
        </Button>
        <Button onClick={toggleFullScreen} className="rounded-full">Fullscreen</Button>
      </div>
    </section>
  );
}
