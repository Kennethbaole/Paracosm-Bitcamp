// UnityComponent.js
import React from "react";
import { Unity, useUnityContext } from "react-unity-webgl";

function UnityComponent() {
  // Configure your Unity build paths here
  const { unityProvider, isLoaded, loadingProgression } = useUnityContext({
    loaderUrl: "/Build/public.loader.js",
    dataUrl: "/Build/public.data.gz",
    frameworkUrl: "/Build/public.framework.js.gz",
    codeUrl: "/Build/public.wasm.gz",
  });

  return (
    <div>
      {!isLoaded && <p>Loading: {Math.round(loadingProgression * 100)}%</p>}
      <Unity unityProvider={unityProvider} style={{ width: "800px", height: "600px" }} />
    </div>
  );
}

export default UnityComponent;
