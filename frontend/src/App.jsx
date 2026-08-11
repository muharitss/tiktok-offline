import { useEffect, useState } from "react"
import VideoItem from "./VideoItem"

const API_URL = "http://localhost:8000"

function App() {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadVideos() {
      try {
        const response = await fetch(`${API_URL}/api/videos`)

        if (!response.ok) {
          throw new Error("Gagal mengambil daftar video")
        }

        const data = await response.json()
        setVideos(data.videos)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadVideos()
  }, [])

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "ArrowDown") {
        event.preventDefault()

        window.scrollBy({
          top: window.innerHeight,
          behavior: "smooth"
        })
      }

      if (event.key === "ArrowUp") {
        event.preventDefault()

        window.scrollBy({
          top: -window.innerHeight,
          behavior: "smooth"
        })
      }
    }

    window.addEventListener("keydown", handleKeyDown)

    return () => {
      window.removeEventListener("keydown", handleKeyDown)
    }
  }, [])

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-black text-white">
        <p>Memuat video...</p>
      </main>
    )
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-black text-white">
        <p>{error}</p>
      </main>
    )
  }

  if (videos.length === 0) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-black text-white">
        <p>Belum ada video.</p>
      </main>
    )
  }

  return (
    <main className="h-screen snap-y snap-mandatory overflow-y-auto bg-black">
      {videos.map((video, index) => (
        <VideoItem
          key={video.name}
          video={video}
          index={index}
          total={videos.length}
        />
      ))}
    </main>
  )
}

export default App