// UnityComponent.js
import React, { useEffect, useState } from "react";
import Unity, { UnityContext } from "react-unity-webgl";

const unityContext = new UnityContext({
  loaderUrl: "public/Build/public.loader.js",      // Adjust based on your build structure
  dataUrl: "public/Build/public.data.gz",      // Adjust based on your build structure
  frameworkUrl: "public/Build/public.framework.js.gz",  // Adjust based on your build structure
  codeUrl: "public/Build/public.wasm.gz",      // Adjust based on your build structure
});

const UnityComponent = () => {
  // Optionally, you can track loading progress or handle events.
  const [loadingProgression, setLoadingProgression] = useState(0);

  useEffect(() => {
    unityContext.on("progress", progression => {
      setLoadingProgression(progression);
    });

    // Optionally clean up listeners on unmount
    return () => {
      unityContext.removeAllEventListeners();
    };
  }, []);

  return (
    <div>
      {loadingProgression < 1 && <p>Loading: {(loadingProgression * 100).toFixed(0)}%</p>}
      <Unity unityContext={unityContext} style={{ width: "800px", height: "600px" }} />
    </div>
  );
};

export default UnityComponent;
