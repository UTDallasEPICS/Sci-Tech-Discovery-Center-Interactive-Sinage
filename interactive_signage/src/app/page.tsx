import Image from "next/image";

export default function Home() {


  return (
  <div className="w-full h-screen grid grid-rows-12 justify-evenly border-amber-200 border-2 ">
    <h1 className="text-center text-7xl border-5 border-amber-200 row-start-3 row-end-5 ">Choose your language</h1>
    <h3 className="text-center text-2xl border-5 border-amber-200 row-start-5  row-end-6">Welcome to the human body adventure</h3>
    <div className="flex justify-evenly gap-48  w-full border-5 border-amber-200 row-start-7 row-end-9">
      <button className="border-3 text-6xl">English</button>
      <button className="border-3 text-6xl">Espanol</button>
      <button className="border-3 text-6xl">Telugu</button>
    </div>

    <h4 className="text-center text-2xl row-start-10 row-end-11 border-5 border-amber-200">Tap to start exploring the amazing human skeleton</h4>

  </div>
  );
}
