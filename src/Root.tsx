import { Composition } from "remotion";
import { WarDollar } from "./war-dollar/WarDollar";

export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="WarDollar"
        component={WarDollar}
        durationInFrames={49051}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
