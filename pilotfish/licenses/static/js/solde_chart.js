fetch("/static/solde_data.json")
    .then(response => response.json())
    .then(rawData => {
        // --- Transformation de tes données en format OHLC attendu ---
        // Exemple : adapter ici en fonction de la structure réelle de ton JSON
        const ohlcData = [];

        for (let i = 0; i < rawData.length; i++) {
            const item = rawData[i];

            // Supposons que chaque item a : date, open, high, low, close dans des indexes ou clés
            // À adapter selon ta structure JSON !
            // Exemple hypothétique (à remplacer par ta logique) :
            // item[0] = date string, item[1] = open, item[2] = high, item[3] = low, item[4] = close
            // Assure-toi que ce soit bien compatible avec ton fichier JSON

            let time = item[0];  // ou item.date
            let open = parseFloat(item[1]);
            let high = parseFloat(item[2]);
            let low = parseFloat(item[3]);
            let close = parseFloat(item[4]);

            if (
                time && !isNaN(open) && !isNaN(high) &&
                !isNaN(low) && !isNaN(close)
            ) {
                ohlcData.push({
                    time: time,       // si besoin convertis en timestamp UNIX : Math.floor(new Date(time).getTime() / 1000)
                    open: open,
                    high: high,
                    low: low,
                    close: close
                });
            }
        }

        // --- Création du graphique ---
        const container = document.getElementById('soldeChartContainer');
        const chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 500,
            layout: {
                backgroundColor: '#ffffff',
                textColor: '#333',
            },
            grid: {
                vertLines: { color: '#eee' },
                horzLines: { color: '#eee' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#ccc',
            },
            timeScale: {
                borderColor: '#ccc',
                timeVisible: true,
                secondsVisible: false,
            },
            localization: {
                dateFormat: 'yyyy-MM-dd',
            }
        });

        // Ajouter la série chandeliers
        const candleSeries = chart.addCandlestickSeries({
            upColor: '#4caf50',
            downColor: '#f44336',
            borderVisible: false,
            wickUpColor: '#4caf50',
            wickDownColor: '#f44336',
        });

        // Injecter les données
        candleSeries.setData(ohlcData);

        // Redimensionnement dynamique
        window.addEventListener('resize', () => {
            chart.applyOptions({ width: container.clientWidth });
        });
    })
    .catch(error => {
        console.error("Erreur lors du chargement ou du traitement du JSON :", error);
    });
