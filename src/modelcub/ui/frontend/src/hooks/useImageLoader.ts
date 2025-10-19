import { useState, useEffect, useRef, useCallback } from "react";
import type { Task } from "@/lib/api/types";

export const useImageLoader = (
  currentTask: Task | null,
  datasetName: string | undefined,
  projectPath: string | null
) => {
  const [isLoading, setIsLoading] = useState(true);
  const cacheRef = useRef(new Map<string, HTMLImageElement>());

  const getImageUrl = useCallback(
    (task: Task | null) => {
      if (!task || !datasetName || !projectPath) return null;
      return `/api/v1/datasets/${datasetName}/image/${
        task.image_path
      }?project_path=${encodeURIComponent(projectPath)}`;
    },
    [datasetName, projectPath]
  );

  const imageUrl = getImageUrl(currentTask);

  const preloadImage = useCallback((url: string): Promise<HTMLImageElement> => {
    if (cacheRef.current.has(url)) {
      return Promise.resolve(cacheRef.current.get(url)!);
    }

    return new Promise((resolve, reject) => {
      const img = new window.Image();
      img.onload = () => {
        // Cache with size limit
        if (cacheRef.current.size >= 10) {
          const firstKey = cacheRef.current.keys().next().value;
          if (firstKey) {
            cacheRef.current.delete(firstKey);
          }
        }
        cacheRef.current.set(url, img);
        resolve(img);
      };
      img.onerror = reject;
      img.src = url;
    });
  }, []);

  // Preload current + next images
  useEffect(() => {
    if (imageUrl) {
      setIsLoading(true);
      preloadImage(imageUrl)
        .then(() => setIsLoading(false))
        .catch(() => {
          console.error("Failed to load image");
          setIsLoading(false);
        });
    }
  }, [imageUrl, preloadImage]);

  const handleImageLoad = useCallback(() => {
    setIsLoading(false);
  }, []);

  const handleImageError = useCallback(() => {
    setIsLoading(false);
    console.error("Failed to load image");
  }, []);

  return {
    imageUrl,
    isLoading,
    handleImageLoad,
    handleImageError,
    cache: cacheRef.current,
  };
};
