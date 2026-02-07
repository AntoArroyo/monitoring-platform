use clap::Parser;
use sysinfo::{System, Disks};
use serde::Serialize;
use chrono::Utc;
use std::time::Duration;

#[derive(Parser)]
struct Args {
    #[arg(long)]
    server_url: String,

    #[arg(long)]
    agent_id: String,
}

#[derive(Serialize)]
struct SystemMetrics {
    cpu_percent: f32,
    ram_percent: f32,
    disk_percent: f32,
    uptime_seconds: u64,
}

#[derive(Serialize)]
struct RaspberryPiMetrics {
    cpu_temp_c: Option<f32>,
}

#[derive(Serialize)]
struct Payload {
    agent_id: String,
    timestamp: String,
    system: SystemMetrics,
    raspberry_pi: RaspberryPiMetrics,
}

const WAIT_SECS: u64 = 5; // dev mode

fn get_pi_temp() -> Option<f32> {
    let path = "/sys/class/thermal/thermal_zone0/temp";
    if let Ok(raw) = std::fs::read_to_string(path) {
        if let Ok(milli) = raw.trim().parse::<f32>() {
            return Some(milli / 1000.0);
        }
    }
    None
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    let client = reqwest::Client::new();

    let mut sys = System::new_all();

    loop {
        sys.refresh_all();

        // CPU
        let cpu = sys.global_cpu_info().cpu_usage();

        // RAM
        let total_mem = sys.total_memory() as f32;
        let used_mem = sys.used_memory() as f32;
        let ram_percent = (used_mem / total_mem) * 100.0;

        // Disk
        let mut disks = Disks::new_with_refreshed_list();
        disks.refresh();
        let disk = disks.iter().next().expect("No disks found");
        let total_disk = disk.total_space() as f32;
        let used_disk = (disk.total_space() - disk.available_space()) as f32;
        let disk_percent = (used_disk / total_disk) * 100.0;

        // Raspberry Pi temp (None on PC, Some on Pi)
        let pi_temp = get_pi_temp();

        let payload = Payload {
            agent_id: args.agent_id.clone(),
            timestamp: Utc::now().to_rfc3339(),
            system: SystemMetrics {
                cpu_percent: cpu,
                ram_percent,
                disk_percent,
                uptime_seconds: System::uptime(),
            },
            raspberry_pi: RaspberryPiMetrics {
                cpu_temp_c: pi_temp,
            },
        };

        let url = format!("{}/api/v1/ingest", args.server_url);

        println!("Sending payload: {:?}", serde_json::to_string_pretty(&payload)?);

        let res = client
            .post(&url)
            .json(&payload)
            .send()
            .await;

        match res {
            Ok(r) => println!("Sent metrics: {}", r.status()),
            Err(e) => eprintln!("Failed to send metrics: {:?}", e),
        }

        tokio::time::sleep(Duration::from_secs(WAIT_SECS)).await;
    }
}
