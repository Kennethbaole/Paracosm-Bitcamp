// UnityComponent.js
import React from "react";
import { Unity, useUnityContext } from "react-unity-webgl";

const UnityComponent = () => {
  const { unityProvider, isLoaded, loadingProgression } = useUnityContext({
    loaderUrl: "/Build/public.loader.js",          // Unity build file in public/Build/
    dataUrl: "/Build/public.data.gz",
    frameworkUrl: "/Build/public.framework.js.gz",
    codeUrl: "/Build/public.wasm.gz",
  });

  return (
    <div>
      {!isLoaded && (
        <p>Loading Unity: {Math.round(loadingProgression * 100)}%</p>
      )}
      <Unity unityProvider={unityProvider} style={{ width: "960px", height: "600px" }} />
    </div>
  );
};

export default UnityComponent;
