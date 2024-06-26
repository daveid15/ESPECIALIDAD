/**
 * Función asíncrona que obtiene las opciones del primer gráfico desde el servidor.
 * @returns {Promise<Object>} Promesa que resuelve a las opciones del gráfico en formato JSON.
 */
const getOptionChart1 = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/ventas/get_chart_data");
      return await response.json();
  } catch (ex) {
      alert(ex);
  }
};

/**
* Función asíncrona que obtiene las opciones del segundo gráfico desde el servidor.
* @returns {Promise<Object>} Promesa que resuelve a las opciones del gráfico en formato JSON.
*/
const getOptionChart2 = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/ventas/get_chart_data_venta");
      return await response.json();
  } catch (ex) {
      alert(ex);
  }
};

/**
* Función asíncrona que obtiene las opciones del tercer gráfico desde el servidor.
* @returns {Promise<Object>} Promesa que resuelve a las opciones del gráfico en formato JSON.
*/
const getOptionChart3 = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/ventas/get_chart_data_completos_bebidas");
      return await response.json();
  } catch (ex) {
      alert(ex);
  }
};

/**
* Inicializa los gráficos utilizando los datos obtenidos del servidor y ECharts.
* @returns {Promise<void>} Promesa que se resuelve una vez que todos los gráficos han sido inicializados.
*/
const initCharts = async () => {
  try {
      // Inicialización de los gráficos usando ECharts
      const chart1 = echarts.init(document.getElementById("chart"));
      const chart2 = echarts.init(document.getElementById("chart2"));
      const chart3 = echarts.init(document.getElementById("chart3"));

      // Obtener opciones de los gráficos desde el servidor y establecerlas
      chart1.setOption(await getOptionChart1());
      chart2.setOption(await getOptionChart2());
      chart3.setOption(await getOptionChart3());

      // Ajustar el tamaño de los gráficos
      chart1.resize();
      chart2.resize();
      chart3.resize();
  } catch (ex) {
      console.error('Error al inicializar los gráficos:', ex);
  }
};

// Escuchar el evento de carga completa de la ventana para iniciar la inicialización de los gráficos
window.addEventListener("load", async () => {
  await initCharts();
});
