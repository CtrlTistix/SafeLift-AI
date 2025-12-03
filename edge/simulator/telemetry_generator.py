"""
Telemetry generator - sends simulated data to backend API.
"""
import asyncio
import aiohttp
from typing import List
from forklift_simulator import ForkliftSimulator
from config import (
    BACKEND_URL,
    NUM_FORKLIFTS,
    WAREHOUSE_BOUNDS,
    OPERATORS,
    EVENT_INTERVAL,
    API_USERNAME,
    API_PASSWORD
)


class TelemetryGenerator:
    """Generates and sends telemetry data to backend."""
    
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.event_interval = EVENT_INTERVAL
        self.access_token = None
        
        # Create forklift simulators
        self.forklifts: List[ForkliftSimulator] = []
        for i in range(1, NUM_FORKLIFTS + 1):
            forklift = ForkliftSimulator(
                forklift_id=i,
                warehouse_bounds=WAREHOUSE_BOUNDS,
                operators=OPERATORS
            )
            self.forklifts.append(forklift)
        
        print(f"🚜 Initialized {NUM_FORKLIFTS} forklift simulators")
    
    async def authenticate(self, session: aiohttp.ClientSession):
        """Authenticate with backend and get access token."""
        try:
            async with session.post(
                f"{self.backend_url}/api/auth/login",
                json={"username": API_USERNAME, "password": API_PASSWORD}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    print(f"✅ Authenticated successfully")
                else:
                    print(f"❌ Authentication failed: {response.status}")
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
    
    async def send_telemetry(self, session: aiohttp.ClientSession, telemetry: dict):
        """Send telemetry data to backend."""
        if not self.access_token:
            return
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with session.post(
                f"{self.backend_url}/api/telemetry",
                json=telemetry,
                headers=headers
            ) as response:
                if response.status == 201:
                    print(f"📡 Telemetry sent: Forklift {telemetry['forklift_id']} - {telemetry['metadata']['scenario']}")
                else:
                    error = await response.text()
                    print(f"⚠️  Failed to send telemetry: {response.status} - {error}")
        except Exception as e:
            print(f"❌ Error sending telemetry: {str(e)}")
    
    async def run(self):
        """Main simulation loop."""
        print(f"🚀 Starting telemetry generator...")
        print(f"📍 Backend URL: {self.backend_url}")
        print(f"⏱️  Update interval: {self.event_interval}s")
        
        async with aiohttp.ClientSession() as session:
            # Authenticate
            await self.authenticate(session)
            
            if not self.access_token:
                print("❌ Cannot proceed without authentication")
                return
            
            # Simulation loop
            iteration = 0
            while True:
                iteration += 1
                print(f"\n--- Iteration {iteration} ---")
                
                # Update all forklifts and send telemetry
                tasks = []
                for forklift in self.forklifts:
                    telemetry = forklift.update(dt=self.event_interval)
                    task = self.send_telemetry(session, telemetry)
                    tasks.append(task)
                
                # Send all telemetry concurrently
                await asyncio.gather(*tasks)
                
                # Wait before next iteration
                await asyncio.sleep(self.event_interval)


async def main():
    """Entry point."""
    generator = TelemetryGenerator()
    await generator.run()


if __name__ == "__main__":
    asyncio.run(main())
