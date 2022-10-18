google.charts.setOnLoadCallback(drawBasicOrigens);

function drawBasicOrigens() {

      var data = google.visualization.arrayToDataTable([
        ['Origens', 'Registros', {role: 'style'}],
        {% for cidade in date_cidades %}
        ['{{cidade.nome}}', {{cidade.qnt}}, '{{cidade.cor}}'],
        {% endfor %}
      ]);

      var options = {
        legend: 'none',
        title: 'Principais origens registradas',        
        Width: '100%',
        height: 1600,
        chartArea: {width: '60%'},
        hAxis: {
          title: '',
          minValue: 0
        },
        vAxis: {
          title: 'Origens'
        }
      };

      var chart_origens = new google.visualization.BarChart(document.getElementById('chart_div_origens'));

      chart_origens.draw(data, options);
    }