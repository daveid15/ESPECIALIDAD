const getOptionChart = async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/proveedores/get_chart_oc_1");
        return await response.json();
    } catch (ex) {
        alert(ex);
    }
  };

const getOptionChart2 = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/proveedores/get_chart_oc_2");
      return await response.json();
  } catch (ex) {
      alert(ex);
  }
};
  
  const initChart = async () => {
    const myChart = echarts.init(document.getElementById("chart_oc1"));
    const myChart2 = echarts.init(document.getElementById("chart_oc2"));
  
    myChart.setOption(await getOptionChart());
    myChart2.setOption(await getOptionChart2());
  
    myChart.resize();
    myChart2.resize();
  };
  
  window.addEventListener("load", async () => {
    await initChart();
  });
  