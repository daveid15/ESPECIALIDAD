const getOptionChart1 = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/ventas/get_chart_data"); // Asegúrate de que la URL apunte al endpoint correcto para el primer gráfico
      return await response.json();
  } catch (ex) {
      alert(ex);
  }
};

const getOptionChart2 = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/ventas/get_chart_data_venta"); // Asegúrate de que la URL apunte al endpoint correcto para el segundo gráfico
      return await response.json();
  } catch (ex) {
      alert(ex);
  }
};

const getOptionChart3 = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/ventas/get_chart_data_completos_bebidas");
      return await response.json();
  } catch (ex) {
      alert(ex);
  }
};

const initCharts = async () => {
  const chart1 = echarts.init(document.getElementById("chart"));
  const chart2 = echarts.init(document.getElementById("chart2"));
  const chart3 = echarts.init(document.getElementById("chart3"));


  chart1.setOption(await getOptionChart1());
  chart2.setOption(await getOptionChart2());
  chart3.setOption(await getOptionChart3());
  
  chart1.resize();
  chart2.resize();
  chart3.resize();
};

window.addEventListener("load", async () => {
  await initCharts();
});
