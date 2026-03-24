import { describe, expect, it } from 'vitest';
import { calculateI2 } from '../pooling';
import { calculateQStatistic } from '../heterogeneity';
import { MetaAnalysis } from '../meta-analysis';

describe('regression checks', () => {
  it('returns I2=0 when df <= 0', () => {
    expect(calculateI2(5, 0)).toBe(0);
    expect(calculateI2(5, -1)).toBe(0);
  });

  it('keeps heterogeneity alias calculateQStatistic available', () => {
    const q = calculateQStatistic([
      { yi: -0.2, vi: 0.04, se: 0.2 },
      { yi: -0.1, vi: 0.05, se: Math.sqrt(0.05) }
    ]);
    expect(q.df).toBe(1);
    expect(Number.isFinite(q.value)).toBe(true);
  });

  it('supports clinical conversion for RD and rejects non-binary measures', () => {
    const rd = new MetaAnalysis(
      [{ yi: -0.1, vi: 0.01, se: 0.1 }],
      { effectMeasure: 'RD', model: 'fixed' }
    );
    rd.pool().clinical({ baselineRisk: 0.2 });
    expect(rd.getResults().clinical?.nnt).toBe(10);

    const smd = new MetaAnalysis(
      [{ yi: -0.3, vi: 0.04, se: 0.2 }],
      { effectMeasure: 'SMD', model: 'fixed' }
    );
    smd.pool();
    expect(() => smd.clinical({ baselineRisk: 0.2 })).toThrow(/supports OR\/logOR, RR\/logRR, or RD/);
  });
});
