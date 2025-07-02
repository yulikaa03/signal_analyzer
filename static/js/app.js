document.addEventListener('DOMContentLoaded', function() {
    // Глобальные обработчики
    
    // Подсветка параметров в алгоритмах
    document.addEventListener('mouseover', function(e) {
        const paramEl = e.target.closest('.algorithm-param');
        if (!paramEl) return;
        
        const signalCode = paramEl.dataset.param;
        const tooltip = document.createElement('div');
        tooltip.className = 'algorithm-tooltip';
        paramEl.appendChild(tooltip);
        
        // Загрузка данных о параметре
        fetch(`/api/signal/${signalCode}`)
            .then(response => response.json())
            .then(data => {
                tooltip.innerHTML = `
                    <div class="tooltip-header">
                        <strong>${data.code}</strong> (${data.format})
                    </div>
                    <div class="tooltip-body">
                        <div><strong>Data Word:</strong> ${data.data_word || 'N/A'}</div>
                        <div><strong>Packet:</strong> ${data.packet || 'N/A'}</div>
                        <div><strong>Bus:</strong> ${data.bus || 'N/A'}</div>
                        ${data.algorithm ? `<div class="algorithm-preview">${highlightAlgorithmParams(data.algorithm)}</div>` : ''}
                    </div>
                `;
                tooltip.style.display = 'block';
            })
            .catch(error => {
                tooltip.innerHTML = 'Error loading signal info';
                tooltip.style.display = 'block';
            });
    });
    
    document.addEventListener('mouseout', function(e) {
        const paramEl = e.target.closest('.algorithm-param');
        if (paramEl) {
            const tooltip = paramEl.querySelector('.algorithm-tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        }
    });
});

function highlightAlgorithmParams(algorithm) {
    if (!algorithm) return '';
    
    // Регулярное выражение для поиска параметров
    const paramRegex = /([A-Z]\d+\.\d+\.\d+)/g;
    
    return algorithm.replace(paramRegex, (match) => {
        return `<span class="algorithm-param" data-param="${match}">${match}</span>`;
    });
}

// Инициализация Vue компонентов
document.querySelectorAll('[data-vue-component]').forEach(el => {
    const componentName = el.dataset.vueComponent;
    
    if (componentName === 'filter-form') {
        createFilterFormComponent(el);
    }
});

function createFilterFormComponent(el) {
    const app = Vue.createApp({
        data() {
            return {
                selectedBus: '',
                selectedPacket: '',
                selectedDataWord: '',
                buses: JSON.parse(el.dataset.buses || '[]'),
                packets: JSON.parse(el.dataset.packets || '[]'),
                dataWords: JSON.parse(el.dataset.dataWords || '[]')
            };
        },
        computed: {
            filteredPackets() {
                if (!this.selectedBus) return this.packets;
                return this.packets.filter(p => p.bus_id == this.selectedBus);
            },
            filteredDataWords() {
                if (!this.selectedPacket) return this.dataWords;
                return this.dataWords.filter(d => d.packet_id == this.selectedPacket);
            }
        },
        methods: {
            resetFilters() {
                this.selectedBus = '';
                this.selectedPacket = '';
                this.selectedDataWord = '';
                this.$emit('filters-changed', {});
            },
            applyFilters() {
                const filters = {};
                if (this.selectedBus) filters.bus_id = this.selectedBus;
                if (this.selectedPacket) filters.packet_id = this.selectedPacket;
                if (this.selectedDataWord) filters.data_word_id = this.selectedDataWord;
                this.$emit('filters-changed', filters);
            }
        }
    });
    
    app.mount(el);
}