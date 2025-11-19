// components/WelcomeScreen.jsx
import Button from "./Button";

const LangaugeSelect = () => {
  return (
    <div className="w-full h-screen grid grid-rows-12 justify-evenly bg-lang-bg bg-contain">
      <h1 className="text-center text-9xl row-start-3 row-end-5 font-title">
        Welcome
      </h1>
      <h3 className="text-center text-2xl border-4 border-style:solid border-amber-200 row-start-5 row-end-6 font-subtitle">
        Welcome to the Human Machine
      </h3>
      <div className="flex justify-evenly gap-48 w-full border-4 border-amber-200 row-start-7 row-end-9">
        <Button mainText={"English"}  color="pink" />
        <button className="border-3 text-6xl font-title">Espanol</button>
        <button className="border-3 text-6xl font-title">Telugu</button>
      </div>
      <h4 className="text-center text-2xl row-start-10 row-end-11 border-5 border-amber-200 font-subtitle">
        Choose your language to explore the amazing human body
      </h4>
    </div>
  );
};

export default LangaugeSelect;