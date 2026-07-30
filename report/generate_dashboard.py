import sqlite3
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
DB_PATH = "storage/niches.db"
OUTPUT_HTML = "report/dashboard.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar-Nicchie Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        h1 {
            color: #2c3e50;
            margin-top: 0;
        }
        .chart-container {
            position: relative;
            height: 500px;
            width: 100%;
        }
        footer {
            margin-top: 40px;
            text-align: center;
            font-size: 0.9em;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Radar-Nicchie: Storico Opportunità</h1>
            <p>Visualizzazione dell'andamento dell'Opportunity Score nel tempo.</p>
        </header>

        <div class="chart-container">
            <canvas id="nicheChart"></canvas>
        </div>

        <footer>
            Generato il: {{generation_date}} | Radar-Nicchie System
        </footer>
    </div>

    <script>
        const rawData = {{data_json}};

        // Elaborazione dati per Chart.js
        const labels = [...new Set(rawData.map(d => d.date))].sort();
        const niches = [...new Set(rawData.map(d => d.niche))];

        const colors = [
            '#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6',
            '#1abc9c', '#e67e22', '#34495e', '#7f8c8d', '#d35400'
        ];

        const datasets = niches.map((niche, index) => {
            return {
                label: niche,
                data: labels.map(date => {
                    const entry = rawData.find(d => d.niche === niche && d.date === date);
                    return entry ? entry.avg_score : null;
                }),
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '22',
                tension: 0.3,
                fill: false
            };
        });

        const ctx = document.getElementById('nicheChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Opportunity Score'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Data di Rilevazione'
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

def generate_dashboard():
    """Genera una dashboard HTML con Chart.js."""
    if not os.path.exists(DB_PATH):
        logger.error("Database non trovato.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = '''
            SELECT niche, date, AVG(score) as avg_score
            FROM niche_signals
            GROUP BY niche, date
            ORDER BY date ASC
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        data = [{"niche": r[0], "date": r[1], "avg_score": r[2]} for r in rows]

        # Sostituzione placeholder nel template
        html_content = HTML_TEMPLATE.replace("{{data_json}}", json.dumps(data))
        html_content = html_content.replace("{{generation_date}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Dashboard generata con successo in {OUTPUT_HTML}")

    except Exception as e:
        logger.error(f"Errore durante la generazione della dashboard: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_dashboard()
