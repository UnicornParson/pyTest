TileComponent = {
  template: `
    <div class="tile" :style="{ backgroundColor: element.color }" @click="toggle">
      <div class="name">{{ element.name }}</div>
      <span class="toggle-icon" v-if="hasChildren">
        {{ isCollapsed ? '+' : '-' }}
      </span>
      <div class="children" v-if="hasChildren && !isCollapsed">
        <tile-component 
          v-for="(child, index) in element.content" 
          :key="index"
          :element="child"
        />
      </div>
    </div>
  `,
  props: ['element'],
  components: {
    TileComponent: () => TileComponent
  },
  setup(props) {
    const isCollapsed = ref(false);
    const hasChildren = ref(props.element.content?.length > 0);

    const toggle = () => {
      if (hasChildren.value) {
        isCollapsed.value = !isCollapsed.value;
      }
    };

    return {
      isCollapsed,
      hasChildren,
      toggle
    };
  }
};

const app = createApp({
    setup() {
      // Load JSON data from a file
      const loadData = async () => {
        try {
          const response = await fetch('/data.json');
          const data = await response.json();
          return ref(data);
        } catch (error) {
          console.error('Error loading JSON:', error);
          return ref({
            color: '#ff0000',
            name: 'Error loading data',
            content: []
          });
        }
      };
  
      const data = await loadData();
  
      return { data };
    },
    components: {
      TileComponent
    }
  });
  
  app.mount('#explorer_app');