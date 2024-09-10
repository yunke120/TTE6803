<template>
    <el-row>
        <el-col :span="24">
            <div class="grid-content ep-bg-purple-dark" />
            <el-space wrap :size="30"> 
            <el-input v-model="ip_as6803" style="width: 300px" placeholder="192.168.0.150" ><template #prepend>AS6803 IP地址：</template> </el-input>
            <el-input v-model="port_as6803" style="width: 150px" placeholder="5000" ><template #prepend>端口：</template> </el-input>
            <el-button type="primary" @click="connectAS6803">连接AS6803</el-button>
            <el-button type="primary" @click="connect8808">连接8808</el-button>
            <el-button type="primary" @click="startTTERecv">开始TTE接收</el-button>
            </el-space>
        </el-col>
    </el-row>

    <el-row>
        <el-col :span="24">
            <div class="grid-content ep-bg-purple-dark" />
            <el-space wrap :size="30"> 
            <el-input v-model="voltage" style="width: 300px" placeholder="2.75V~4.0V" ><template #prepend>设置AS6803电压值：</template> 
                <template #append>V</template>
            </el-input>
            <el-button type="primary" @click="setVoltage">设置电压</el-button>
            <el-button type="primary" @click="incVoltage">增加电压(10mV)</el-button>
            <el-button type="primary" @click="decVoltage">减小电压(10mV)</el-button>
            <!-- 当前锂电模拟器输出电压：{{voltage}} -->
        </el-space>
        </el-col>
    </el-row>
</template>


<script setup>
import { ref, inject, onMounted, onBeforeUnmount  } from 'vue';
import { ElMessage } from 'element-plus'
import { useSharedStore } from '../store/useSharedStore';
const store = useSharedStore();
const voltage_set = store.sharedVoltage;

const ip_as6803 = ref('192.168.0.150')
const port_as6803 = ref('5000')
const voltage = ref(3.8)

const socket = inject('socket'); // 从全局注入 socket 实例

const isBtnDisabled = ref(false); // 按钮使能状态

const connectAS6803 = () => {
    // console.log(ip, port);
    socket.emit('connect_as6803', {'ip': ip_as6803.value, 'port': port_as6803.value});
};

const connect8808 = () => {
    socket.emit('connect_8808')
}

const startTTERecv = () => {
    socket.emit('start_tte_recv')
}

const setVoltage = () => {
    socket.emit('set_voltage', {'voltage': voltage.value});
    store.setSharedVoltage(voltage.value);
};

const incVoltage = () => {
    let temp = voltage.value + 0.010
    console.log(temp);
    
    socket.emit('inc_voltage', {'voltage': temp}, (reponse) => {
        console.log(reponse);
        if(reponse == true)
        {
            voltage.value = temp;
            store.setSharedVoltage(temp);
            ElMessage('设置成功')
        }
        else
        {
            ElMessage('设置失败')
        }

    });
};

const decVoltage = () => {
   let  temp = voltage.value - 0.010
    socket.emit('dec_voltage', {'voltage': temp}, (reponse) => {
        console.log(reponse);
        if(reponse == true)
        {
            voltage.value = temp;
            store.setSharedVoltage(temp);
            ElMessage('设置成功')
        }
        else
        {
            ElMessage('设置失败')
        }
    });
};

onMounted(() => {
  socket.on('log_msg', (data) => {
    ElMessage(data);
  });

  socket.on('connect', (data) => {
    ElMessage('服务器已连接')
    // isBtnDisabled.value = true;
  });
  socket.on('disconnect', (data) => {
    ElMessage('服务器断开连接');
    //  isBtnDisabled.value = false;
  });
});

onBeforeUnmount(() => {
  socket.disconnect();
});

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