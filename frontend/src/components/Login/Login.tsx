import Navbar from "../Layout/Navbar";


export default function LoginPage(){
    return(
        <>
            <Navbar />
            <div className="container mx-auto">
                {/* <div className="grid grid-cols-4 text-center gap-4">
                    <div>01</div>
                    <div>02</div>
                    <div>03</div>
                    <div>04</div>
                    <div>05</div>
                    <div>06</div>
                    <div>07</div>
                    <div>08</div>
                    <div>09</div>
                    <div>10</div>
                </div>
                <br />
                <button className="btn btn-neutral">Neutral</button> */}
                {/* <div className="flex flex-col items-center justify-center">
                    <div className="w-full bg-white rounded-lg shadow dark:border">
                        <div className="p-6 space-y-4">
                            <a href="#" className="mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
                                <img className="w-8 h-8 mr-2" src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg" alt="logo" />
                                Flowbite
                            </a>

                            <label htmlFor="email" className="block text-sm font-medium text-gray-900 dark:text-white">Your email</label>
                            <input type="email" name="email" placeholder="name@company.com" className="input input-bordered w-full max-w-xs" />

                            <label htmlFor="password" className="block text-sm font-medium text-gray-900 dark:text-white">Password</label>
                            <input type="password" name="password" placeholder="*****" className="input input-bordered w-full max-w-xs" />
                        </div>
                    </div>
                </div> */}

                <div className="flex flex-col items-center justify-center">
                    
                    <form className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                        <h1 className="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
                            Log in
                        </h1>
                        <br />
                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                                Username
                            </label>
                            <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" placeholder="Username" />
                        </div>
                        <div className="mb-6">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                                Password
                            </label>
                            <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" id="password" type="password" placeholder="******************" />
                        </div>
                        <div className="flex items-center justify-between">
                            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="button">
                                Sign In
                            </button>
                        {/* <a className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800" href="#">
                            Forgot Password?
                        </a> */}
                        </div>
                    </form>
                <p className="text-center text-gray-500 text-xs">
                    &copy;2024 EMS. All rights reserved.
                </p>
                </div>

            </div>
        </>
    )
}