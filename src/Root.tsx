import { Composition } from "remotion";
import { InventionOfTheCoin } from "./invention-of-the-coin/InventionOfTheCoin";
import { GoldBecameMoney } from "./gold-became-money/GoldBecameMoney";

export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="InventionOfTheCoin"
        component={InventionOfTheCoin}
        durationInFrames={40478}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="GoldBecameMoney"
        component={GoldBecameMoney}
        durationInFrames={51549}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
