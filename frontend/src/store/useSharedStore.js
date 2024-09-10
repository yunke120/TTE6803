
import { defineStore } from 'pinia';

export const useSharedStore = defineStore('voltage', {
  state: () => ({
    sharedVoltage: 3.8,
  }),
  actions: {
    setSharedVoltage(newVal) {
      this.sharedVoltage = newVal;
    },
  },
});
