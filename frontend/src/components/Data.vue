<template>
    <el-row :gutter="50">
        <el-col :span="6">
            <div class="grid-content ep-bg-purple" />
            <el-table :data="TelemetryValue1" stripe style="width: 100%"  :cell-style="cellStyle">
                <el-table-column prop="name" label="遥测名称" width="180" />
                <el-table-column prop="value" label="遥测值" width="180" />
            </el-table>
        </el-col>
        <el-col :span="6">
            <div class="grid-content ep-bg-purple" />
            <el-table :data="TelemetryValue2" stripe style="width: 100%"  :cell-style="cellStyle">
                <el-table-column prop="name" label="遥测名称" width="180" />
                <el-table-column prop="value" label="遥测值" width="180" />
            </el-table>
        </el-col>
        <el-col :span="6">
            <div class="grid-content ep-bg-purple" />
            <el-table :data="TelemetryValue3" stripe style="width: 100%">
                <el-table-column prop="name" label="遥测名称" width="180" />
                <el-table-column prop="value" label="遥测值" width="180" />
            </el-table>
        </el-col>
    </el-row>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue';
import { useSharedStore } from '../store/useSharedStore';

const socket = inject('socket'); // 从全局注入 socket 实例
const store = useSharedStore(); 
const voltage_set = store.sharedVoltage;

const TelemetryValue1 = ref([])
const TelemetryValue2 = ref([])
const TelemetryValue3 = ref([])

// 接收遥测数据
onMounted(() => {
    socket.on('telemetry_value', (data) => {
        // console.log(data);
        
        TelemetryValue1.value = data.slice(0, 11); // 分割数据
        TelemetryValue2.value = data.slice(11,22);
        TelemetryValue3.value = data.slice(22);
    });
});

// 遥测值超出6mV显示红色
const cellStyle = ({ row, column, rowIndex, columnIndex }) => {
    if (column.property === 'value' && row.value > (voltage_set+0.006) && row.value < (voltage_set-0.006)) {
        return { backgroundColor: 'red', color: 'white' };
    }
    return {};
};

</script>