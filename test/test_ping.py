import asyncio
import redis

async def test_redis():
    try:
        # Connect to the Redis server using redis-py
        redis_client = redis.Redis(host='localhost', port=6379)

        # Execute the PING command with proper formatting (newline at the end)
        pong_response = await redis_client.ping()
        print(f"Received response: {pong_response}")

        # Assert the expected response for a successful test
        assert pong_response == "*1\r\n$4\r\nPONG\r\n"
        print("Test successful!")
    except (ConnectionError, redis.exceptions.ConnectionError) as e:
        print(f"Error connecting to Redis: {e}")

async def main():
    await test_redis()

if __name__ == "__main__":
    asyncio.run(main())