<template>
    <el-row>
        <el-col :span="24">
            <div class="grid-content ep-bg-purple-dark" />
            <el-space wrap :size="30">
                <el-input v-model="ip_as6803" style="width: 300px" placeholder="192.168.0.150"
                    input-style="text-align: center;"><template #prepend>AS6803 IP地址：</template>
                </el-input>
                <el-input v-model="port_as6803" style="width: 150px" placeholder="5000"
                    input-style="text-align: center;"><template #prepend>端口：</template> </el-input>

                <el-button type="primary" @click="toggleConnectAS6803">
                    {{ isConnectAs6803 ? '断开AS6803' : '连接AS6803' }}
                </el-button>

                <el-button type="primary" @click="toggleConnect8808">
                    {{ isConnect8808 ? '断开8808' : '连接8808' }}
                </el-button>


                <el-button type="primary" @click="startTTERecv">开始TTE接收</el-button>
            </el-space>
        </el-col>
    </el-row>

    <el-row>
        <el-col :span="24">
            <div class="grid-content ep-bg-purple-dark" />
            <el-space wrap :size="30">
                <el-input v-model="voltage" style="width: 300px" placeholder="2.75V~4.0V"
                    input-style="text-align: center;"><template #prepend>设置AS6803电压值：</template>
                    <template #append>V</template>
                </el-input>
                <el-button type="primary" @click="setVoltage">设置电压</el-button>
                <el-button type="primary" @click="incVoltage">增加电压(10mV)</el-button>
                <el-button type="primary" @click="decVoltage">减小电压(10mV)</el-button>
                <!-- 当前锂电模拟器输出电压：{{voltage}} -->
            </el-space>
        </el-col>
    </el-row>

    <el-row>
        <el-col :span="24">
            <div class="grid-content ep-bg-purple-dark" />
            <el-space wrap :size="30">
                <el-input v-model="saveInterval" style="width: 300px" placeholder="20"
                    input-style="text-align: center;"><template #prepend>数据保存帧间隔：</template>
                    <template #append>帧</template>
                </el-input>
                <el-button type="primary" @click="setSaveFrameInterval">
                    设置数据保存间隔时间
                </el-button>
            </el-space>
        </el-col>
    </el-row>

    <el-row>
        <el-col :span="24">
            <div class="grid-content ep-bg-purple-dark" />
            <el-space wrap :size="30">
                <el-input v-model="timing" style="width: 300px" placeholder="20"
                    input-style="text-align: center;"><template #prepend>定时时间：</template>
                    <template #append>s</template>
                </el-input>
                <el-button type="primary" @click="toggleScheduler">
                    {{ isSchedulerRunning ? '关闭定时任务' : '开启定时任务' }}
                </el-button>
            </el-space>
        </el-col>
    </el-row>
</template>


<script setup>
import { ref, inject, onMounted, onBeforeUnmount } from 'vue';
import { ElMessage } from 'element-plus'
import { useSharedStore } from '../store/useSharedStore';
const store = useSharedStore();
const voltage_set = store.sharedVoltage;
const isSchedulerRunning = ref(false);
const isConnectAs6803 = ref(false);
const isConnect8808 = ref(false);
const ip_as6803 = ref('192.168.0.150')
const port_as6803 = ref('5000')
const voltage = ref(3.8)
const timing = ref(20)
const saveInterval = ref(10)
const socket = inject('socket'); // 从全局注入 socket 实例


const connectAS6803 = () => {
    console.log("连接AS6803");
    socket.emit('connect_as6803', { 'ip': ip_as6803.value, 'port': port_as6803.value });
};

const disconnectAS6803 = () => {
    console.log("断开AS6803");
    socket.emit('close_as6803');
};

const toggleConnectAS6803 = () => {
    if (isConnectAs6803.value) {
        connectAS6803();
    } else {
        disconnectAS6803();
    }
    isConnectAs6803.value = !isConnectAs6803.value;
};

const connect8808 = () => {
    console.log("连接8808");
    socket.emit('connect_8808');
};

const disconnect8808 = () => {
    console.log("断开8808");
    socket.emit('close_8808');
};

const toggleConnect8808 = () => {
    if (isConnect8808.value) {
        connect8808();
    } else {
        disconnect8808();
    }
    isConnect8808.value = !isConnect8808.value;
};


const startTTERecv = () => {
    console.log("开始接收TTE数据");
    socket.emit('start_tte_recv')
}

const setVoltage = () => {
    console.log("设置电压值");
    socket.emit('set_voltage', { 'voltage': voltage.value });
    store.setSharedVoltage(voltage.value);
};

const incVoltage = () => {
    let temp = voltage.value + 0.010
    console.log("增大电压值");

    socket.emit('inc_voltage', { 'voltage': temp }, (reponse) => {
        console.log(reponse);
        if (reponse == true) {
            voltage.value = temp;
            store.setSharedVoltage(temp);
            // ElMessage('设置成功')
        }
        else {
            // ElMessage('设置失败')
        }

    });
};

const decVoltage = () => {
    console.log("减小电压值");
    let temp = voltage.value - 0.010
    socket.emit('dec_voltage', { 'voltage': temp }, (reponse) => {
        console.log(reponse);
        if (reponse == true) {
            voltage.value = temp;
            store.setSharedVoltage(temp);
            // ElMessage('设置成功')
        }
        else {
            // ElMessage('设置失败')
        }
    });
};

onMounted(() => {
    socket.on('log_msg', (data) => {
        ElMessage(data);
    });

    socket.on('connect', (data) => {
        ElMessage({
            message: '服务器已连接.',
            type: 'success',
        })

    });
    socket.on('disconnect', (data) => {
        ElMessage.error('服务器断开连接.')
    });
});

onBeforeUnmount(() => {
    socket.disconnect();
});


const setSaveFrameInterval = () => {
    console.log("设置保存数据间隔");
    socket.emit('set_save_interval', { 'interval': saveInterval.value });
}

const startScheduler = () => {
    console.log("定时任务已开启");
    socket.emit('start_scheduler', { 'timing': timing.value });
};

const stopScheduler = () => {
    console.log("定时任务已关闭");
    socket.emit('stop_scheduler');
};

const toggleScheduler = () => {
    if (isSchedulerRunning.value) {
        stopScheduler();
    } else {
        startScheduler();
    }
    isSchedulerRunning.value = !isSchedulerRunning.value;
};

</script>


<style lang="scss">
.el-row {
    margin-bottom: 20px;
}

.el-row:last-child {
    margin-bottom: 0;
}

.el-col {
    border-radius: 4px;
}

.grid-content {
    border-radius: 4px;
    min-height: 36px;
}
</style>