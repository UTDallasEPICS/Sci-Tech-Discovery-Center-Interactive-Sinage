function Button({mainText, subText, color}){
    return(
        <button className={`rounded-md bg-pink border-2 border-solid bg-cover m-10 text-left`}>
            <p className="font-title text-6xl">
                {mainText}
                {subText}
            </p>

        </button>
    )
}
export default Button