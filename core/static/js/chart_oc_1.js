/**
 * Función asíncrona que obtiene las opciones del gráfico desde el servidor.
 * @returns {Promise<Object>} Promesa que resuelve a las opciones del gráfico en formato JSON.
 */
const getOptionChart = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/proveedores/get_chart_oc_1");
      return await response.json();
  } catch (ex) {
      alert(ex);
  }
};

/**
* Inicializa el gráfico utilizando los datos obtenidos del servidor y ECharts.
* @returns {Promise<void>} Promesa que se resuelve una vez que el gráfico ha sido inicializado.
*/
const initChart = async () => {
  try {
      // Inicialización del gráfico usando ECharts
      const myChart = echarts.init(document.getElementById("chart_oc1"));
      
      // Obtener opciones del gráfico desde el servidor y establecerlas
      myChart.setOption(await getOptionChart());
      
      // Ajustar el tamaño del gráfico
      myChart.resize();
  } catch (ex) {
      console.error('Error al inicializar el gráfico:', ex);
  }
};

// Escuchar el evento de carga completa de la ventana para iniciar la inicialización del gráfico
window.addEventListener("load", async () => {
  await initChart();
});
