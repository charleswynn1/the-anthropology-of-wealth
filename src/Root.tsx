import { Composition } from "remotion";
import { TenDollarDay } from "./ten-dollar-day/TenDollarDay";
import { HundredKTippingPoint } from "./hundred-k-tipping-point/HundredKTippingPoint";
import { BudgetAtAnyIncome } from "./budget-at-any-income/BudgetAtAnyIncome";
import { WhyMoneyFeelingTight } from "./why-money-feels-tight/WhyMoneyFeelingTight";
import { OriginOfDebt } from "./origin-of-debt/OriginOfDebt";

export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="TenDollarDay"
        component={TenDollarDay}
        durationInFrames={8148}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="HundredKTippingPoint"
        component={HundredKTippingPoint}
        durationInFrames={19516}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="BudgetAtAnyIncome"
        component={BudgetAtAnyIncome}
        durationInFrames={10271}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="WhyMoneyFeelingTight"
        component={WhyMoneyFeelingTight}
        durationInFrames={13226}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="OriginOfDebt"
        component={OriginOfDebt}
        durationInFrames={20962}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
