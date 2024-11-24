import asyncio
import time
import config

async def standard_inputs():
    print("testing standard input")
    return "quit"

async def unethical_inputs():
    print("testing Unethical input")
    return "quit"

#test_type = 1
#print("\n name 1:", __name__)
#if __name__ == "__main__":
#    import user
#    print("1: test_type is:", test_type)
#    asyncio.run(user.main())
#    
#test_type = 2
#print("\n name 2:", __name__)
#if __name__ == "__main__":
#    import user
#    print("2: test_type is:", test_type)
#    asyncio.run(user.main())

async def main():
    import user
    config.test_type = 1
    while not config.global_quit:
        await user.main()
    config.test_type = 2
    config.global_quit = False
    while not config.global_quit:
        await user.main()

if __name__ == "__main__":
    asyncio.run(main())
