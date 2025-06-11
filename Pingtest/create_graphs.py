import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

def create_ping_graphs(csv_file: str = "ping_results.csv"):
    """Create graphs from ping monitoring data"""
    
    if not os.path.exists(csv_file):
        print(f"CSV file '{csv_file}' not found. Run the ping monitor first.")
        return
    
    try:
        # Read the CSV data
        df = pd.read_csv(csv_file)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter successful pings only
        successful_pings = df[df['status'] == 'success'].copy()
        successful_pings['ping_time_ms'] = pd.to_numeric(successful_pings['ping_time_ms'])
        
        if successful_pings.empty:
            print("No successful ping data found.")
            return
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Ping Monitoring Results', fontsize=16)
        
        # 1. Time series plot
        ax1 = axes[0, 0]
        for target in successful_pings['target'].unique():
            target_data = successful_pings[successful_pings['target'] == target]
            ax1.plot(target_data['timestamp'], target_data['ping_time_ms'], 
                    label=target, marker='o', markersize=2, alpha=0.7)
        
        ax1.set_title('Ping Times Over Time')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Ping Time (ms)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 2. Box plot comparison
        ax2 = axes[0, 1]
        targets = []
        ping_data = []
        for target in successful_pings['target'].unique():
            target_data = successful_pings[successful_pings['target'] == target]
            targets.append(target)
            ping_data.append(target_data['ping_time_ms'].values)
        
        ax2.boxplot(ping_data, labels=targets)
        ax2.set_title('Ping Time Distribution')
        ax2.set_ylabel('Ping Time (ms)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Success rate over time (hourly)
        ax3 = axes[1, 0]
        df_hourly = df.copy()
        df_hourly['hour'] = df_hourly['timestamp'].dt.floor('H')
        
        success_rates = []
        hours = []
        for target in df['target'].unique():
            target_hourly = df_hourly[df_hourly['target'] == target].groupby('hour').agg({
                'status': ['count', lambda x: (x == 'success').sum()]
            }).round(2)
            
            target_hourly.columns = ['total', 'successful']
            target_hourly['success_rate'] = (target_hourly['successful'] / target_hourly['total']) * 100
            
            ax3.plot(target_hourly.index, target_hourly['success_rate'], 
                    label=f'{target}', marker='o', markersize=4)
        
        ax3.set_title('Success Rate Over Time (Hourly)')
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Success Rate (%)')
        ax3.set_ylim(0, 105)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        # 4. Histogram of ping times
        ax4 = axes[1, 1]
        for target in successful_pings['target'].unique():
            target_data = successful_pings[successful_pings['target'] == target]
            ax4.hist(target_data['ping_time_ms'], bins=20, alpha=0.7, label=target)
        
        ax4.set_title('Ping Time Distribution (Histogram)')
        ax4.set_xlabel('Ping Time (ms)')
        ax4.set_ylabel('Frequency')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the plot
        output_file = f"ping_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Graph saved as: {output_file}")
        
        # Show statistics
        print("\n--- Ping Statistics ---")
        for target in successful_pings['target'].unique():
            target_data = successful_pings[successful_pings['target'] == target]
            total_pings = len(df[df['target'] == target])
            successful = len(target_data)
            success_rate = (successful / total_pings) * 100 if total_pings > 0 else 0
            
            print(f"\n{target}:")
            print(f"  Total attempts: {total_pings}")
            print(f"  Successful: {successful}")
            print(f"  Success rate: {success_rate:.1f}%")
            
            if not target_data.empty:
                print(f"  Average ping: {target_data['ping_time_ms'].mean():.1f}ms")
                print(f"  Min ping: {target_data['ping_time_ms'].min():.1f}ms")
                print(f"  Max ping: {target_data['ping_time_ms'].max():.1f}ms")
                print(f"  Std deviation: {target_data['ping_time_ms'].std():.1f}ms")
        
        plt.show()
        
    except Exception as e:
        print(f"Error creating graphs: {e}")

if __name__ == "__main__":
    create_ping_graphs()
